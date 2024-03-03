import json

from django.db import models
from django.template.response import TemplateResponse
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

class Dashboard(Page):
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


class  CustomFormBuilder(FormBuilder):
    def get_create_field_function(self, type):
        create_field_function = super().get_create_field_function(type)

        def wrapped_create_field_function(field, options):
            created_field = create_field_function(field, options)
            created_field.widget.attrs.update({
                "placeholder": field.placeholder,
            })
            return created_field

        return wrapped_create_field_function


class PromptPage(AbstractForm):
    form_builder = CustomFormBuilder

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
        #MultiFieldPanel(FormField.content_panels),
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