import decimal
import json
import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from modelcluster.fields import ParentalKey
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.contrib.forms.models import (AbstractForm, AbstractFormField,
                                          AbstractFormSubmission)
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.contrib.forms.utils import get_field_clean_name
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page

import genai.llm_client
from genaiappbuilder import settings

from .dynamodb import MentorSessionDDB, MentorSessionHistoryDDB


class MentorSession:
    def __init__(self, create_date, runnable_output, page_title, mentor_url):
        self.create_date = create_date
        self.runnable_output = runnable_output
        self.page_title = page_title
        self.mentor_url = mentor_url


class Dashboard(LoginRequiredMixin, Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        exclusive_start_key_create_date = request.GET.get("exclusive_start_key")
        if exclusive_start_key_create_date is not None and exclusive_start_key_create_date != "null":
            exclusive_start_key = {
                "create_date": int(exclusive_start_key_create_date),
                "user_id": request.user.id
            }
            context['previous_evaluated_key'] = exclusive_start_key_create_date
        else:
            exclusive_start_key = None

        mentor_session_ddb = MentorSessionDDB()
        response = mentor_session_ddb.query_with_paging(request.user.id, 20, exclusive_start_key)

        mentor_session = []
        for item in response["Items"]:
            mentoring_data = json.loads(item["mentoring_data"])

            mentor_url = ""
            page_title = ""
            if "page_id" in mentoring_data:
                page = Page.objects.get(id=int(mentoring_data["page_id"]))
                mentor_url = f"{page.url}?openId={int(item['create_date'])}"
                page_title = page.title

            mentor_session.append(
                MentorSession(int(item["create_date"]), mentoring_data["runnable_output"], page_title, mentor_url))

        context['mentor_session'] = mentor_session
        last_evaluated_key = response.get("LastEvaluatedKey")
        if last_evaluated_key:
            del response["LastEvaluatedKey"]["user_id"]
            context['last_evaluated_key'] = last_evaluated_key["create_date"]

        # add more data to context if needed

        return context

    def serve(self, request, *args, **kwargs):
        # if user is not authenticated
        if not request.user.is_authenticated:
            # make a redirect to login page
            return redirect('account_login')
        context = self.get_context(request, *args, **kwargs)
        response = super().serve(request, *args, **kwargs)
        previous_evaluated_key = context.get("previous_evaluated_key")
        if previous_evaluated_key:
            response["X-Previous-Evaluated-Key"] = previous_evaluated_key
        last_evaluated_key = context.get("last_evaluated_key")
        if last_evaluated_key:
            response["X-Last-Evaluated-Key"] = last_evaluated_key

        return response


class MentorIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]


class ProviderIndexPage(Page):
    intro = RichTextField(blank=True)

    openai_instructions = RichTextField(blank=True)
    aws_bedrock_instructions = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('openai_instructions'),
        FieldPanel('aws_bedrock_instructions'),
    ]

    template = "genai_app/provider/provider_index_page.html"


class ChatPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]


# look at this https://www.coderedcorp.com/blog/adding-placeholder-text-to-wagtail-forms/
class FormField(AbstractFormField):
    page = ParentalKey('PromptPage', on_delete=models.CASCADE, related_name='form_fields')


class CustomFormField(AbstractFormField):
    page = ParentalKey(
        "PromptPage",
        on_delete=models.CASCADE,
        related_name="custom_form_fields",
    )

    # add custom field to FormField model
    placeholder = models.CharField(
        "Placeholder",
        max_length=254,
        blank=True,
    )

    field_name = models.CharField(
        "Fieldname",
        max_length=254,
        blank=False,
    )

    # enable our custom field in the admin UI
    panels = AbstractFormField.panels + [
        FieldPanel("placeholder"),
        FieldPanel("field_name"),
    ]

    def get_field_clean_name(self):
        return get_field_clean_name(self.field_name)


class CustomFormBuilder(FormBuilder):
    def get_create_field_function(self, type):
        create_field_function = super().get_create_field_function(type)

        def wrapped_create_field_function(field, options):
            created_field = create_field_function(field, options)
            created_field.widget.attrs.update({
                "placeholder": field.placeholder,
            })
            return created_field

        return wrapped_create_field_function


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super().default(o)


class PromptPage(AbstractForm):
    form_builder = CustomFormBuilder

    intro = RichTextField(blank=True)

    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
    ])

    prompts = StreamField([
        ('prompt_list', blocks.ListBlock(blocks.StructBlock([
            ('prompt_id', blocks.CharBlock()),
            ('prompt_text', blocks.TextBlock()),
        ]))),
    ], blank=True, null=True)

    content_panels = Page.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('prompts'),
        InlinePanel('custom_form_fields', label="Custom form fields"),
    ]

    runnable_output = ""

    def get_submission_class(self):
        return CustomFormSubmission

    def process_form_submission(self, form):
        # TODO save to DynamoDB
        submission = self.get_submission_class().objects.create(
            form_data=form.cleaned_data,
            page=self, user=form.user
        )
        return submission

    def get_form_fields(self):
        return self.custom_form_fields.all()

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        open_id = self.request.GET.get('openId')
        if open_id:
            history_id = self.request.GET.get('historyId')
            if history_id:
                mentor_session_history_ddb = MentorSessionHistoryDDB()
                response = mentor_session_history_ddb.get_item(
                    {
                        'mentor_session_id': f"{self.request.user.id}-{open_id}",
                        'history_date': int(history_id)
                    }
                )
            else:
                mentor_session_ddb = MentorSessionDDB()
                response = mentor_session_ddb.get_item(
                    {
                        'user_id': self.request.user.id,
                        'create_date': int(open_id)
                    }
                )
            mentoring_data = json.loads(response["mentoring_data"])

            self.runnable_output = mentoring_data["runnable_output"]
            form.initial = mentoring_data["form_data"]

        return form

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["runnable_output"] = self.runnable_output
        open_id = request.GET.get("openId")
        if open_id:
            context["open_id"] = open_id
        return context

    def history_view(self, request):
        history = None
        open_id = request.GET.get("openId")
        if open_id:
            history = self.get_mentor_session_history(request.user.id, open_id)
        # Render template
        return render(request, 'genai_app/mentor_session_history.html', {'history': history})

    # Override the serve method
    def serve(self, request, *args, **kwargs):
        self.request = request
        view = request.GET.get("view")
        if view is not None and view == 'history_view':
            return self.history_view(request)
        else:
            return super().serve(request, *args, **kwargs)

    def render_landing_page(self, request, form_submission=None, *args, **kwargs):
        context = self.get_context(request)
        context["form_submission"] = form_submission
        model_parameters = {'max_tokens_to_sample': int(request.POST["max_tokens"]),
                            "temperature": float(request.POST["temperature"]),
                            "top_k": int(request.POST["top_k"]),
                            "top_p": int(request.POST["top_p"]),
                            "stop_sequences": ["\n\nHuman"]
                            }

        org_provider_id = 1
        llm_client = genai.llm_client.LLMClient(model="gpt-3.5-turbo", org_provider_id=org_provider_id,
                                                lite_llm_api_key=self.request.user.lite_llm_api_key)
        prompt = llm_client.create_prompt(self.prompts.raw_data[0]["value"][0]["value"]["prompt_text"],
                                          **form_submission.form_data)

        response = llm_client.complete(prompt)
        context["runnable_output"] = response

        mentoring_data = {
            'page_id': self.id,
            'model_parameters': model_parameters,
            'form_data': form_submission.form_data,
            'runnable_output': response
        }
        mentoring_data_json = json.dumps(mentoring_data, cls=DecimalEncoder)

        mentor_session_ddb = MentorSessionDDB()

        # Get user_id from request
        user_id = request.user.id

        # Check if we already have a mentor_session running
        session_create_date_string = request.GET.get('openId')
        if session_create_date_string is not None and session_create_date_string != "":
            create_date = int(session_create_date_string)
            mentor_session_ddb.update(user_id, create_date, mentoring_data_json)
        else:
            # Get current UTC time in seconds since 1970
            create_date = int(time.time())
            mentor_session_ddb.insert(user_id, create_date, mentoring_data_json)

        context["history"] = self.get_mentor_session_history(user_id, create_date)
        context["open_id"] = create_date
        response = TemplateResponse(
            request, self.get_landing_page_template(request), context
        )
        return response

    def get_mentor_session_history(self, user_id, create_date):
        # Get latest history
        mentor_session_id = f"{user_id}-{create_date}"
        mentor_session_history_ddb = MentorSessionHistoryDDB()
        history_ddb = mentor_session_history_ddb.query_with_paging(mentor_session_id, 10, None)
        history = []
        for item in history_ddb["Items"]:
            history_mentoring_data = json.loads(item["mentoring_data"])
            history.append({"create_date": create_date, "history_date": item["history_date"],
                            "runnable_output": history_mentoring_data["runnable_output"],
                            "mentor_url": f"{self.url}?openId={create_date}&historyId={item['history_date']}"})
        return history


class CustomFormSubmission(AbstractFormSubmission):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
