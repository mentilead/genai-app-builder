import logging

import boto3
import openai
from boto3.exceptions import Boto3Error
from langchain_core.prompts import PromptTemplate

from genai_app.models import OrgProvider
from genaiappbuilder import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Class for interacting with the LiteLLM API."""

    def __init__(self, model: str, org_provider_id: int, lite_llm_api_key: str) -> None:
        """
        Initialize the class.

        :param model: The name of the model to use.
        :type model: str

        :param org_provider_id: The ID of the organization provider to use for LLM calls.
        :type org_provider_id: int

        :param lite_llm_api_key: The API key for Lite LLM.
        :type lite_llm_api_key: str
        """
        self.model = model
        self.org_provider_id = org_provider_id
        self.extra_body = self._create_extra_body()
        self.client = openai.OpenAI(
            api_key=lite_llm_api_key,
            base_url=settings.LITE_LLL_BASE_URL,
        )

    def _create_extra_body(self) -> dict:
        """
        Create extra body for the litellm API call.

        :return: extra body as a dictionary.
        """
        try:
            org_provider = OrgProvider.objects.get(id=self.org_provider_id)
        except OrgProvider.DoesNotExist:
            raise ValueError("Provider ID does not exist for {self.org_provider_id}.")

        if org_provider.provider == "OPENAI":
            if not org_provider.val1:
                raise ValueError("For OPENAI provider, Provider value 1 is required.")
            return {"api_key": org_provider.val1}  # We pass in the OpenAI API Key
        elif org_provider.provider == "AWS_BEDROCK":
            # We use the IAM ARN Role and ExternalID to get credentials for a boto3 client
            # Based on this blog post:
            # https://aws.amazon.com/blogs/apn/securely-using-external-id-for-accessing-aws-accounts-owned-by-others/
            if not org_provider.val1 or not org_provider.val2 or not org_provider.val3:
                raise ValueError("For AWS_BEDROCK provider, values 1, 2 and 3 are required.")
            try:
                sts_client = boto3.client('sts')
                assumed_role_object = sts_client.assume_role(
                    RoleArn=org_provider.val1,
                    RoleSessionName="AssumeRoleSession1",
                    ExternalId=org_provider.val2
                )
            except Boto3Error as e:
                raise ValueError(f"Failed to assume role: {str(e)}")

            credentials = assumed_role_object['Credentials']

            return {
                "aws_access_key_id": credentials['AccessKeyId'],
                "aws_secret_access_key": credentials['SecretAccessKey'],
                "aws_session_token": credentials['SessionToken'],
                "aws_region_name": org_provider.val3}

        else:
            raise ValueError("Invalid provider")

    @staticmethod
    def create_prompt(prompt_template: str, **arg_dict) -> str:
        """Format the input prompt_template with the keyword arguments
           The keyword arguments come from the **arg_dict"""

        multi_var_prompt = PromptTemplate(
            input_variables=list(arg_dict.keys()),
            template=prompt_template
        )
        # Pass in values to the input variables
        prompt: str = multi_var_prompt.format(**arg_dict)
        return prompt

    def complete(self, prompt: str) -> str:
        response = self.client.chat.completions.create(model=self.model, messages=[
            {
                "role": "user",
                "content": prompt
            },
        ],
            extra_body=self.extra_body)

        return response.choices[0].message.content
