import re
import uuid

from django import forms
from django.core.exceptions import ValidationError
from django.forms import TextInput

from core.models import UserProfile
from .models import OrgProvider


class OpenAIAPIKeyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # pop the user from kwargs
        self.user = kwargs.pop('user', None)
        super(OpenAIAPIKeyForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        """
            names must be unique per organization, provider
        :return:
        """
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError('Name is required')
        profile = UserProfile.objects.select_related('organization').get(user=self.user)
        org_openai = OrgProvider.openai.filter(name=name, organization=profile.organization)

        # We are allowed to update and keep same name
        if self.instance.pk:
            org_openai = org_openai.exclude(pk=self.instance.pk)

        if org_openai.exists():
            raise ValidationError("Name must be unique for your organization's list of OpenAI API Keys")

        return name

    def clean_val1(self):
        val1 = self.cleaned_data.get('val1')
        if not val1:
            raise ValidationError('OpenAI API Key is required')
        return val1

    class Meta:
        model = OrgProvider
        fields = "__all__"
        exclude = ['organization', 'provider', 'create_date', 'val2', 'val3']

        labels = {
            'val1': 'OpenAI API Key',
        }
        help_texts = {
            'name': 'Human-friendly label for the OpenAI API Key.',
        }


class AWSBedrockForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # pop the user from kwargs
        self.user = kwargs.pop('user', None)
        super(AWSBedrockForm, self).__init__(*args, **kwargs)

        if not self.instance.pk:
            # Set the initial value of field1 to a new UUID
            self.fields['val2'].initial = uuid.uuid4()

    def clean_name(self):
        """
            names must be unique per organization, provider
        :return:
        """
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError('Name is required')
        profile = UserProfile.objects.select_related('organization').get(user=self.user)
        org_aws_bedrock = OrgProvider.aws_bedrock.filter(name=name, organization=profile.organization)

        # We are allowed to update and keep same name
        if self.instance.pk:
            org_aws_bedrock = org_aws_bedrock.exclude(pk=self.instance.pk)

        if org_aws_bedrock.exists():
            raise ValidationError("Name must be unique for your organization's list of AWS IAM Role ARNs")

        return name

    def clean_val1(self):
        val1 = self.cleaned_data.get('val1')
        if not val1:
            raise ValidationError('AWS IAM Role ARN is required')
        if not re.match(r"arn:aws:iam::[0-9]{12}:role/[a-zA-Z0-9+=,.@_-]{1,64}", val1):
            raise forms.ValidationError("Input is not a valid AWS IAM Role ARN.")
        return val1

    def clean_val2(self):
        val2 = self.cleaned_data.get('val2')
        if not val2:
            raise ValidationError('External ID is required')
        return val2

    def clean_val3(self):
        val3 = self.cleaned_data.get('val3')
        if not val3:
            raise ValidationError('AWS region is required')
        return val3

    class Meta:
        model = OrgProvider
        fields = "__all__"
        exclude = ['organization', 'provider', 'create_date']

        labels = {
            'val1': 'AWS IAM Role ARN',
            'val2': 'External ID',
            'val3': 'AWS Region',
        }
        help_texts = {
            'name': 'Human-friendly label for the AWS Role ARN registration.',
            'val1': 'ARN from AWS IAM Role created in your AWS account.',
            'val2': 'External ID is used to grant access from one AWS role to another.',
            'val3': 'AWS region that will be used for the Bedrock service.',
        }

        widgets = {
            'val1': TextInput(attrs={'placeholder': 'arn:aws:iam::123456789012:role/iam-role-name'}),
            'val3': TextInput(attrs={'placeholder': 'us-east-1'}),
        }