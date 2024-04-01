from django.urls import path
from .views import (openai_org_api_key_list_view, aws_bedrock_org_iam_role_arn_list_view,
                    org_provider_create_view, org_provider_update_view, org_provider_delete_view)

app_name = 'genai_app'  # add this line

urlpatterns = [
    path('providers/openai_org_api_key/list', openai_org_api_key_list_view, name='openai_org_api_key_list'),
    path('providers/aws_bedrock_org_iam_role_arn/list', aws_bedrock_org_iam_role_arn_list_view,
         name='aws_bedrock_org_iam_role_arn_list'),
    path('providers/org_provider/create', org_provider_create_view, name='org_provider_create_view'),
    path('providers/org_provider/<int:pk>/update', org_provider_update_view,
         name='org_provider_update_view'),
    path('providers/org_provider/<int:pk>/delete', org_provider_delete_view,
         name='org_provider_delete_view'),
]
