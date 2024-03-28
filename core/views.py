import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views import View
from django.shortcuts import render, redirect
from django.views.generic import FormView, ListView, TemplateView
from django.views.generic.edit import FormMixin

from .forms import LLMAPIKeyForm
from .models import LLMAPIKey, UserProfile, LLMAPIKey
from .forms import OrganizationForm


class UIPlaygroundView(View):
    template_name = 'ui_playground.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


ui_playground_view = UIPlaygroundView.as_view()


class OrganizationView(FormView, LoginRequiredMixin):
    template_name = 'core/organization.html'
    form_class = OrganizationForm


    def get_success_url(self):
        return reverse('core:organization')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        organization = user_profile.organization
        context['organization'] = organization
        context['form'] = self.form_class(instance=organization)  # Initialize form with organization instance
        return context

    def post(self, request, *args, **kwargs):
        user_profile = UserProfile.objects.get(user=self.request.user)
        organization = user_profile.organization
        form = self.form_class(data=request.POST, instance=organization)  # Bind form with POST data and organization instance
        if form.is_valid():
            organization = form.save()
            # Re-initialize form with newly saved organization instance
            form = self.form_class(instance=organization)
            return self.render_to_response(self.get_context_data(form=form))
        else:
            return self.form_invalid(form)


organization_view = OrganizationView.as_view()


class LLMAPIKeyListView(ListView, LoginRequiredMixin):
    model = LLMAPIKey
    template_name = 'core/api_keys_list.html'
    context_object_name = 'api_keys'

    def get_queryset(self):
        user_profile_organization = self.request.user.userprofile.organization
        return super().get_queryset().filter(organization=user_profile_organization)


llm_api_keys_list_view = LLMAPIKeyListView.as_view()


class LLMAPIKeyListAdd(FormView, LoginRequiredMixin):
    model = LLMAPIKey
    form_class = LLMAPIKeyForm
    template_name = 'core/api_keys_form.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        profile = UserProfile.objects.select_related('organization').get(user=self.request.user)
        obj.organization = profile.organization
        obj.save()
        return HttpResponse(
            status=204,
            headers={
                'HX-Trigger': json.dumps({
                    "apiKeysListChanged": None
                })
            })

    def get_form_kwargs(self):
        kwargs = super(LLMAPIKeyListAdd, self).get_form_kwargs()
        # update the kwargs with user
        kwargs.update({'user': self.request.user})
        return kwargs


llm_api_keys_add_view = LLMAPIKeyListAdd.as_view()


class LLMAPIKeyView(TemplateView, LoginRequiredMixin):
    template_name = 'core/api_keys.html'


llm_api_keys_view = LLMAPIKeyView.as_view()
