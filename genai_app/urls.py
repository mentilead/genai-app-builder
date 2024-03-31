from django.urls import path
from .views import (openai_org_api_key_list_view, openai_org_api_key_create_view, openai_org_api_key_update_view,
                    aws_bedrock_org_iam_role_arn_list_view, aws_bedrock_org_role_arn_create_view,
                    aws_bedrock_org_role_arn_update_view)

app_name = 'genai_app'  # add this line

urlpatterns = [
    path('providers/openai_org_api_key/list', openai_org_api_key_list_view, name='openai_org_api_key_list'),
    path('providers/openai_org_api_key/add', openai_org_api_key_create_view, name='openai_org_api_key_create_view'),
    path('providers/openai_org_api_key/<int:pk>/edit', openai_org_api_key_update_view,
         name='openai_org_api_key_update_view'),

    path('providers/aws_bedrock_org_iam_role_arn/list', aws_bedrock_org_iam_role_arn_list_view,
         name='aws_bedrock_org_iam_role_arn_list'),
    path('providers/aws_bedrock_org_iam_role_arn/add', aws_bedrock_org_role_arn_create_view, name='aws_bedrock_org_role_arn_create_view'),
    path('providers/aws_bedrock_org_iam_role_arn/<int:pk>/edit', aws_bedrock_org_role_arn_update_view,
         name='aws_bedrock_org_role_arn_update_view'),

]
