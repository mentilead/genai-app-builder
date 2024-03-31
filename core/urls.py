from django.urls import path
from .views import organization_view, llm_api_keys_view, llm_api_keys_list_view, llm_api_keys_add_view, llm_api_keys_edit_view, llm_api_keys_remove_view

app_name = 'core'  # add this line

urlpatterns = [
    path('organization', organization_view, name='organization'),
    path('api-keys', llm_api_keys_view, name='api_keys'),
    path('api-keys/list', llm_api_keys_list_view, name='api_keys_list'),
    path('api-keys/add', llm_api_keys_add_view, name='api_keys_add'),
    path('api-keys/<int:pk>/remove', llm_api_keys_remove_view, name='api_keys_remove'),
    path('api-keys/<int:pk>/edit', llm_api_keys_edit_view, name='api_keys_edit'),
]
