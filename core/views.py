import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import View
from django.shortcuts import render, redirect
from django.views.generic import FormView

from .models import UserProfile
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
        form = self.form_class(data=request.POST,
                               instance=organization)  # Bind form with POST data and organization instance
        if form.is_valid():
            organization = form.save()
            # Re-initialize form with newly saved organization instance
            form = self.form_class(instance=organization)
            return self.render_to_response(self.get_context_data(form=form))
        else:
            return self.form_invalid(form)


organization_view = OrganizationView.as_view()

