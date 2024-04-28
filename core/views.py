from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import FormView

from .forms import OrganizationForm


class UIPlaygroundView(View):
    template_name = 'ui_playground.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


ui_playground_view = UIPlaygroundView.as_view()


class OrganizationView(FormView, LoginRequiredMixin):
    """
    View for managing organization details.
    Inherits from FormView and LoginRequiredMixin.

    Attributes:
        template_name (str): Name of the template to render.
        form_class (Form): Class of the form to be used.

    Methods:
        get_success_url: Returns the URL to redirect to after successful form submission.
        get_context_data: Returns the context data to be passed to the template.
        post: Handles POST requests and processes the form data.
    """
    template_name = 'core/organization.html'
    form_class = OrganizationForm

    def get_success_url(self):
        return reverse('core:organization')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = self.request.user.organization
        context['organization'] = organization
        context['form'] = self.form_class(instance=organization)  # Initialize form with organization instance
        return context

    def post(self, request, *args, **kwargs):
        organization = self.request.user.organization
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
