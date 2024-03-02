import os
from typing import Optional

import boto3
from botocore.config import Config
from langchain.llms.bedrock import Bedrock


class BedrockClientManager:
    MAX_TOKENS = 4096
    TEMPERATURE = 0.5
    TOP_K = 250
    TOP_P = 1
    STOP_SEQUENCES = ["\n\nHuman"]

    def __init__(self, model_id, model_kwargs):
        boto3_bedrock = self._get_bedrock_client()
        self.textgen_llm = self._init_textgen_llm(boto3_bedrock, model_id, model_kwargs)

    def _init_textgen_llm(self, boto3_bedrock, model_id, model_kwargs):

        return Bedrock(model_id=model_id,
                       client=boto3_bedrock,
                       model_kwargs=model_kwargs,
                       streaming=True
                       )

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


# multi_var_prompt = PromptTemplate(input_variables=["theName"],
#                                   template="Human: Say Hello to {theName} Assistant:")
# prompt = multi_var_prompt.format(theName="Bob the Builder")
#
# bcm = BedrockClientManager()
# response = bcm.textgen_llm.invoke(input=prompt)
# print(response)
