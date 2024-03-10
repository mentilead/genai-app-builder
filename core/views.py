from django.views import View
from django.shortcuts import render


class UIPlaygroundView(View):
    template_name = 'ui_playground.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


ui_playground_view = UIPlaygroundView.as_view()
