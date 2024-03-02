import environ
import os

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


class OpenAIClientManager:
    MAX_TOKENS = 10
    TEMPERATURE = 0.5

    def __init__(self, openai_api_key, model_id, model_kwargs):
        self.MAX_TOKENS = model_kwargs.get('max_tokens', self.MAX_TOKENS)
        self.TEMPERATURE = model_kwargs.get('temperature', self.TEMPERATURE)

        self.textgen_llm = ChatOpenAI(openai_api_key=openai_api_key,
                                      model=model_id,
                                      temperature=self.TEMPERATURE,
                                      max_tokens=self.MAX_TOKENS)

