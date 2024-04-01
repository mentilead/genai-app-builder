from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from .models import Organization


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
