from django import forms
from django.forms.models import modelformset_factory
from .models import LLMConfig, Organization


class LLMConfigForm(forms.ModelForm):
    class Meta:
        model = LLMConfig
        fields = "__all__"
        exclude = ['user']


LLMConfigFormSet = modelformset_factory(LLMConfig, form=LLMConfigForm, extra=2, max_num=2)


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