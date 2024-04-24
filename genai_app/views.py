import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import ListView, CreateView, UpdateView
from django.views.generic.edit import FormMixin, DeleteView

from .forms import OpenAIAPIKeyForm, AWSBedrockForm
from .models import OrgProvider


class OpenAIOrgAPIKeyListView(LoginRequiredMixin, ListView):
    model = OrgProvider
    template_name = 'genai_app/provider/openai_apikey_list.html'
    context_object_name = 'openai_keys'

    def get_queryset(self):
        user_organization = self.request.user.organization
        return OrgProvider.openai.filter(organization=user_organization)


openai_org_api_key_list_view = OpenAIOrgAPIKeyListView.as_view()


class AWSBedrockOrgIAMRoleARNKeyListView(LoginRequiredMixin, ListView):
    model = OrgProvider
    template_name = 'genai_app/provider/aws_bedrock_iam_role_arn_list.html'
    context_object_name = 'aws_iam_role_arns'

    def get_queryset(self):
        user_organization = self.request.user.organization
        return OrgProvider.aws_bedrock.filter(organization=user_organization)


aws_bedrock_org_iam_role_arn_list_view = AWSBedrockOrgIAMRoleARNKeyListView.as_view()


class OrgProviderBaseForm(LoginRequiredMixin, FormMixin):
    model = OrgProvider
    template_name = 'genai_app/provider/provider_form.html'
    provider_type: OrgProvider.Provider = None

    def dispatch(self, request, *args, **kwargs):
        self.provider_type = request.GET.get('provider_type')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        if pk is not None:
            try:
                OrgProvider.objects.get(pk=pk, organization=self.request.use.organization)
            except OrgProvider.DoesNotExist:
                return HttpResponseForbidden("You are not allowed to view this resource.")

        return super().get(request, *args, **kwargs)

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

        # Ensure the user's organization matches what's being saved
        if obj.id and obj.organization and obj.organization != self.request.user.organization:
            raise ValueError('The selected organization does not correspond to the users organization')

        # Prevent an update if the organization already exists
        if not obj.id:
            obj.organization = self.request.user.organization

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


org_provider_create_view = OrgProviderCreateView.as_view()
org_provider_update_view = OrgProviderUpdateView.as_view()


class OrgProviderRemove(LoginRequiredMixin, DeleteView):
    model = OrgProvider
    template_name = 'genai_app/provider/provider_remove.html'

    def dispatch(self, request, *args, **kwargs):
        self.provider_type = request.GET.get('provider_type')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object.delete()
        if self.provider_type == OrgProvider.Provider.OPENAI:
            change_trigger = 'openAIAPIKeyListChanged'
        elif self.provider_type == OrgProvider.Provider.AWS_BEDROCK:
            change_trigger = 'awsBedrockIAMRoleArnListChanged'
        else:
            raise ValueError(f"Invalid provider type: {self.provider_type}")

        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    f"{change_trigger}": None
                })
            })

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset.filter(organization=self.request.user.organization)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.provider_type == OrgProvider.Provider.OPENAI:
            context['provider_registration_type'] = 'OpenAI API Key'
        elif self.provider_type == OrgProvider.Provider.AWS_BEDROCK:
            context['provider_registration_type'] = 'AWS Bedrock Role ARN'
        else:
            raise ValueError(f"Invalid provider type: {self.provider_type}")
        return context


org_provider_delete_view = OrgProviderRemove.as_view()
