from django.urls import path
from .views import organization_view

app_name = 'core'  # add this line

urlpatterns = [
    path('organization', organization_view, name='organization'),
]
