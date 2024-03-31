import json
import os
from typing import Optional

import boto3
from botocore.config import Config
from langchain.llms.bedrock import Bedrock
from langchain_core.prompts import PromptTemplate

from genaiappbuilder import settings


class BedrockClientManager:
    MAX_TOKENS = 4096
    TEMPERATURE = 0.5
    TOP_K = 250
    TOP_P = 1
    STOP_SEQUENCES = ["\n\nHuman"]

    def __init__(self, model_id, model_kwargs):
        self.boto3_bedrock = self._get_bedrock_client_customer()
        self.textgen_llm = self._init_textgen_llm(self.boto3_bedrock, model_id, model_kwargs)

    def _init_textgen_llm(self, boto3_bedrock, model_id, model_kwargs):

        return Bedrock(model_id=model_id,
                       client=boto3_bedrock,
                       model_kwargs=model_kwargs,
                       streaming=True
                       )

    def _get_bedrock_client_customer(runtime: Optional[bool] = True):
        target_region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION"))
        print(f"Create new client\n  Using region: {target_region}")
        session_kwargs = {"region_name": target_region}
        client_kwargs = {**session_kwargs}
        sts_client = boto3.client('sts', region_name=target_region)
        # Call the assume_role method of the STSConnection object and pass the role
        # ARN,external ID and a role session name.
        assumed_role_object = sts_client.assume_role(
            RoleArn=settings.env('AWS_ROLE_ARN'),
            RoleSessionName="AssumeRoleSession1",
            ExternalId=settings.env('AWS_EXTERNAL_ID')
        )
        # From the response that contains the assumed role, get the temporary
        # credentials that can be used to make subsequent API calls
        credentials = assumed_role_object['Credentials']
        retry_config = Config(
            region_name=target_region,
            retries={
                "max_attempts": 10,
                "mode": "standard",
            },
        )
        session = boto3.Session(region_name=target_region,
                                aws_access_key_id=credentials['AccessKeyId'],
                                aws_secret_access_key=credentials['SecretAccessKey'],
                                aws_session_token=credentials['SessionToken']
                                )
        if runtime:
            service_name = 'bedrock-runtime'
        else:
            service_name = 'bedrock'

        bedrock_client = session.client(
            service_name=service_name,
            config=retry_config,
            **client_kwargs
        )

        print("boto3 Bedrock client successfully created!")
        print(bedrock_client._endpoint)
        return bedrock_client



    def _get_bedrock_client(runtime: Optional[bool] = True):
        target_region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION"))

        print(f"Create new client\n  Using region: {target_region}")
        session_kwargs = {"region_name": target_region}
        client_kwargs = {**session_kwargs}

        profile_name = os.environ.get("AWS_PROFILE")
        if profile_name:
            print(f"  Using profile: {profile_name}")
            session_kwargs["profile_name"] = profile_name

        retry_config = Config(
            region_name=target_region,
            retries={
                "max_attempts": 10,
                "mode": "standard",
            },
        )
        session = boto3.Session(**session_kwargs)

        if runtime:
            service_name = 'bedrock-runtime'
        else:
            service_name = 'bedrock'

        bedrock_client = session.client(
            service_name=service_name,
            config=retry_config,
            **client_kwargs
        )

        print("boto3 Bedrock client successfully created!")
        print(bedrock_client._endpoint)
        return bedrock_client

    @staticmethod
    def create_prompt(prompt_template: str, **arg_dict: dict):
        multi_var_prompt = PromptTemplate(
            input_variables=list(arg_dict.keys()),
            template=prompt_template
        )

        # Pass in values to the input variables
        prompt = multi_var_prompt.format(**arg_dict)
        return prompt



    @staticmethod
    def create_claude_body(messages=[
        {"role": "user", "content": "Hello!"}
    ],
                           token_count=150,
                           temp=0,
                           topP=1,
                           topK=250,
                           stop_sequence=["Human"]):
        """
        Simple function for creating a body for Anthropic Claude models.
        """
        body = {
            "messages": messages,
            "max_tokens": token_count,
            "temperature": temp,
            "anthropic_version": "",
            "top_k": topK,
            "top_p": topP,
            "stop_sequences": stop_sequence
        }
        return body

    def get_claude_response(self, messages="",
                            token_count=250,
                            temp=0,
                            topP=1,
                            topK=250,
                            stop_sequence=["Human:"],
                            model_id="anthropic.claude-3-sonnet-20240229-v1:0"):
        """
        Simple function for calling Claude via boto3 and the invoke_model API.
        """
        body = self.create_claude_body(messages=messages,
                                       token_count=token_count,
                                       temp=temp,
                                       topP=topP,
                                       topK=topK,
                                       stop_sequence=stop_sequence)
        response = self.boto3_bedrock.invoke_model(modelId=model_id, body=json.dumps(body))
        response = json.loads(response['body'].read().decode('utf-8'))
        return response

    # prompt = [{"role": "user", "content": "tell me a story"}]
    # model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    # text_resp = get_claude_response(messages=prompt,
    #                                 token_count=250,
    #                                 temp=0,
    #                                 topP=1,
    #                                 topK=0,
    #                                 stop_sequence=["Human:"],
    #                                 model_id=model_id)
    # print(text_resp)

# multi_var_prompt = PromptTemplate(input_variables=["theName"],
#                                   template="Human: Say Hello to {theName} Assistant:")
# prompt = multi_var_prompt.format(theName="Bob the Builder")
#
# bcm = BedrockClientManager()
# response = bcm.textgen_llm.invoke(input=prompt)
# print(response)
