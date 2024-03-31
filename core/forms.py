from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from .models import LLMAPIKey, Organization, LLMAPIKey, UserProfile


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = "__all__"
        exclude = ['api_id', ]
        labels = {
            'name': 'Organization name',
        }
        help_texts = {
            'name': 'Human-friendly label for your organization, shown in user interfaces',
        }


class LLMAPIKeyForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # pop the user from kwargs
        self.user = kwargs.pop('user', None)
        super(LLMAPIKeyForm, self).__init__(*args, **kwargs)

    def clean_api_key_name(self):
        """
            api key names must be unique per organization
        :return:
        """
        api_key_name = self.cleaned_data.get('api_key_name')
        profile = UserProfile.objects.select_related('organization').get(user=self.user)
        api_keys = LLMAPIKey.objects.filter(api_key_name=api_key_name, organization=profile.organization)

        # We are allowed to update and keep same name
        if self.instance.pk:
            api_keys = api_keys.exclude(pk=self.instance.pk)

        if api_keys.exists():
            raise ValidationError('Name must be unique for your organization')

        return api_key_name

    def clean_secret_key(self):
        secret_key = self.cleaned_data.get('secret_key')
        if self.cleaned_data.get('provider_name') == "aws_bedrock" and not secret_key:
            raise ValidationError('Secret key is required for AWS Bedrock')
        return secret_key

    class Meta:
        model = LLMAPIKey
        fields = "__all__"
        exclude = ['organization', 'create_date', ]

        labels = {
            'api_key_name': 'Name',
        }
        help_texts = {
            'api_key_name': 'Human-friendly label for the GenAI provider registration',
        }
