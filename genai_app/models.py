import decimal
import json
from datetime import datetime, timezone


import boto3
from boto3.dynamodb.conditions import Key

from django.db import models
from django.template.response import TemplateResponse
from django.utils import timezone as django_timezone
from modelcluster.fields import ParentalKey
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.contrib.forms.models import AbstractFormField, AbstractFormSubmission, AbstractEmailForm, AbstractForm
from wagtail.contrib.forms.panels import FormSubmissionsPanel

from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.forms.utils import get_field_clean_name

from genaiappbuilder import settings

from genai.providers.bedrock import BedrockClientManager


class UserMentoring:
    def __init__(self, create_date, runnable_output, mentor_url):
        self.create_date = create_date
        self.runnable_output = runnable_output
        self.mentor_url = mentor_url


class Dashboard(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        dynamodb = boto3.resource('dynamodb', region_name='fakeRegion', endpoint_url='http://localhost:4000')
        table = dynamodb.Table('UserMentoring')

        response = table.query(
            KeyConditionExpression=Key('user_id').eq(request.user.id),
            ScanIndexForward=False,  # This parameter makes the sorting in descending order
            Limit=10  # Limit parameter for paging. Modify limit as per your requirements
        )

        user_mentoring = []
        for item in response["Items"]:
            print(item["create_date"])
            # Convert integer timestamp to datetime in UTC
            create_date_utc = datetime.utcfromtimestamp(int(item["create_date"])).replace(tzinfo=timezone.utc)

            # Convert the UTC datetime to the user's timezone
            create_date_user_tz = create_date_utc.astimezone(django_timezone.get_default_timezone())

            # Format the datetime as a string
            string_create_date = create_date_user_tz.strftime('%Y-%m-%d %H:%M:%S')
            document = json.loads(item["document"])

            mentor_url = ""
            if "page_id" in document:
                page = Page.objects.get(id=int(document["page_id"]))
                mentor_url = f"{page.url}?openId={int(item['create_date'])}"

            print(mentor_url)
            user_mentoring.append(UserMentoring(string_create_date, document["runnable_output"], mentor_url))

        context['user_mentoring'] = user_mentoring

        # add more data to context if needed

        return context

class MentorIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]


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
        return super(DecimalEncoder, self).default(o)

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
            print(open_id)
            dynamodb = boto3.resource('dynamodb', region_name='fakeRegion', endpoint_url='http://localhost:4000')
            table = dynamodb.Table('UserMentoring')
            response = table.get_item(
                Key={
                    'user_id': self.request.user.id,
                    'create_date': int(open_id)
                }
            )
            document = json.loads(response['Item']["document"])

            print(document["form_data"])
            form.initial = document["form_data"]

        return form

    # Override the serve method
    def serve(self, request, *args, **kwargs):
        self.request = request
        return super().serve(request, *args, **kwargs)

    def render_landing_page(self, request, form_submission=None, *args, **kwargs):
        """
        Renders the landing page.

        You can override this method to return a different HttpResponse as
        landing page. E.g. you could return a redirect to a separate page.
        """
        context = self.get_context(request)
        context["form_submission"] = form_submission
        print(self.prompts.raw_data[0]["value"][0]["value"]["prompt_id"])
        print(self.prompts.raw_data[0]["value"][0]["value"]["prompt_text"])
        print(form_submission)

        model_parameters = {'max_tokens_to_sample': int(request.POST["max_tokens"]),
                            "temperature": float(request.POST["temperature"]),
                            "top_k": int(request.POST["top_k"]),
                            "top_p": int(request.POST["top_p"]),
                            "stop_sequences": ["\n\nHuman"]
                            }

        print(model_parameters)

        prompt = BedrockClientManager.create_prompt(self.prompts.raw_data[0]["value"][0]["value"]["prompt_text"],
                                                    **form_submission.form_data)
        client = BedrockClientManager("anthropic.claude-v2:1", model_kwargs=model_parameters)

        response = client.textgen_llm.invoke(input=prompt)
        print(response)
        context["runnable_output"] = response

        import boto3
        import time
        import json

        # Get user_id from request
        user_id = request.user.id

        # Get current UTC time in seconds since 1970
        create_date = int(time.time())

        # Let's consider this as your JSON document to be saved in DynamoDB
        mentoring_data = {
            'page_id': self.id,
            'model_parameters': model_parameters,
            'form_data': form_submission.form_data,
            'runnable_output': response
        }

        # Convert your data into JSON string
        mentoring_data_json = json.dumps(mentoring_data, cls=DecimalEncoder)

        dynamodb = boto3.resource('dynamodb', region_name='fakeRegion', endpoint_url='http://localhost:4000')
        table = dynamodb.Table('UserMentoring')
        print(f"PageID: {self.id}")
        response = table.put_item(
            Item={
                'user_id': user_id,  # Converting user_id to String as DynamoDB requires it in String format
                'create_date': create_date,
                'document': mentoring_data_json
            }
        )

        # Rest of your code...


        # for chunk in response:
        #    print(chunk, end="", flush=True)

        return TemplateResponse(
            request, self.get_landing_page_template(request), context
        )


class CustomFormSubmission(AbstractFormSubmission):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class CustomForm(AbstractForm):
    template = 'forms/custom_form_page.html'

    body = RichTextField(blank=True)

    content_panels = AbstractForm.content_panels + [
        FieldPanel('body', classname="full"),
        # MultiFieldPanel(FormField.content_panels),
    ]

    def process_form_submission(self, form):
        # You can add your own logic here to process the form data
        # This method is called when a form is submitted
        pass

    def serve_post(self, request, *args, **kwargs):
        form = self.get_form(request.POST, page=self, user=request.user)

        if form.is_valid():
            # Perform your custom saving action here.
            # You can omit calling `process_form_submission` if you want to skip storing in AbstractFormSubmission.
            self.process_form_submission(form)
            return self.render_landing_page(request, form=form, reset=True)

        return self.render(request, self.get_context(request, form=form))
