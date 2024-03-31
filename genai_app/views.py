import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView
from django.views.generic.edit import FormMixin

from core.models import UserProfile
from .forms import OpenAIAPIKeyForm, AWSBedrockForm
from .models import OrgProvider


class OpenAIOrgAPIKeyListView(LoginRequiredMixin, ListView):
    model = OrgProvider
    template_name = 'genai_app/provider/openai_apikey_list.html'
    context_object_name = 'openai_keys'

    def get_queryset(self):
        user_profile_organization = self.request.user.userprofile.organization
        return OrgProvider.openai.filter(organization=user_profile_organization)


openai_org_api_key_list_view = OpenAIOrgAPIKeyListView.as_view()


class AWSBedrockOrgIAMRoleARNKeyListView(LoginRequiredMixin, ListView):
    model = OrgProvider
    template_name = 'genai_app/provider/aws_bedrock_iam_role_arn_list.html'
    context_object_name = 'aws_iam_role_arns'

    def get_queryset(self):
        user_profile_organization = self.request.user.userprofile.organization
        return OrgProvider.aws_bedrock.filter(organization=user_profile_organization)


aws_bedrock_org_iam_role_arn_list_view = AWSBedrockOrgIAMRoleARNKeyListView.as_view()


class OrgProviderBaseForm(LoginRequiredMixin, FormMixin):
    model = OrgProvider
    template_name = 'genai_app/provider/provider_form.html'
    provider_type: OrgProvider.Provider = None

    def dispatch(self, request, *args, **kwargs):
        self.provider_type = request.GET.get('provider_type')
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        if self.provider_type == OrgProvider.Provider.OPENAI:
            return OpenAIAPIKeyForm
        elif self.provider_type == OrgProvider.Provider.AWS_BEDROCK:
            return AWSBedrockForm
        else:
            raise ValueError(f"Invalid provider type: {self.provider_type}")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # update the kwargs with user
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.provider_type == OrgProvider.Provider.OPENAI:
            context['provider_registration_type'] = 'OpenAI API Key'
        elif self.provider_type == OrgProvider.Provider.AWS_BEDROCK:
            context['provider_registration_type'] = 'AWS Bedrock Role ARN'
        else:
            raise ValueError(f"Invalid provider type: {self.provider_type}")
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)

        if self.provider_type == OrgProvider.Provider.OPENAI:
            obj.provider = OrgProvider.Provider.OPENAI
            change_trigger = 'openAIAPIKeyListChanged'
        elif self.provider_type == OrgProvider.Provider.AWS_BEDROCK:
            obj.provider = OrgProvider.Provider.AWS_BEDROCK
            change_trigger = 'awsBedrockIAMRoleArnListChanged'
        else:
            raise ValueError(f"Invalid provider type: {self.provider_type}")

        profile = UserProfile.objects.select_related('organization').get(user=self.request.user)
        obj.organization = profile.organization
        obj.save()

        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    f"{change_trigger}": None
                })
            })


class OrgProviderCreateView(OrgProviderBaseForm, CreateView):
    pass


class OrgProviderUpdateView(OrgProviderBaseForm, UpdateView):
    pass


openai_org_api_key_create_view = OrgProviderCreateView.as_view()
openai_org_api_key_update_view = OrgProviderUpdateView.as_view()

aws_bedrock_org_role_arn_create_view = OrgProviderCreateView.as_view()
aws_bedrock_org_role_arn_update_view = OrgProviderUpdateView.as_view()
