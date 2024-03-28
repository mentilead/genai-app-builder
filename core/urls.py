from django.urls import path
from .views import organization_view, llm_api_keys_view, llm_api_keys_list_view, llm_api_keys_add_view

app_name = 'core'  # add this line

urlpatterns = [
    path('organization', organization_view, name='organization'),
    path('api-keys', llm_api_keys_view, name='api_keys'),
    path('api-keys/list', llm_api_keys_list_view, name='api_keys_list'),
    path('api-keys/add', llm_api_keys_add_view, name='api_keys_add'),
]
