import environ
import os
import json
from django.http import StreamingHttpResponse
from ninja import Router
from genai.providers import bedrock, openai

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

environ.Env.read_env(os.path.join('../.env'))

openai.api_key = env("OPENAI_API_KEY")

router = Router()


async def async_auth(request):
    return True


@router.get("/stream", auth=async_auth)
async def create_stream(request):
    user_content = request.GET.get('content', '')  # Get the content from the query parameter

    async def event_stream():
        MAX_TOKENS = 4096
        TEMPERATURE = 0.5
        TOP_K = 250
        TOP_P = 1
        STOP_SEQUENCES = ["\n\nHuman"]

        model_parameters = {'max_tokens_to_sample': MAX_TOKENS,
                            "temperature": TEMPERATURE,
                            "top_k": TOP_K,
                            "top_p": TOP_P,
                            "stop_sequences": STOP_SEQUENCES
                            }

        client = bedrock.BedrockClientManager("anthropic.claude-v2:1", model_kwargs=model_parameters)

        response = client.textgen_llm.stream(input=f"Human: {user_content} Assistant:")
        for chunk in response:
            print(chunk, end="", flush=True)
            yield f'data: {chunk}\\n\\n'

        print("finished in event_stream")

    print("before StreamingHttpResponse")
    response = StreamingHttpResponse(event_stream(), content_type=" text/event-stream")
    print("after StreamingHttpResponse")

    response['X-Accel-Buffering'] = 'no'  # Disable buffering in nginx
    response['Cache-Control'] = 'no-cache'  # Ensure clients don't cache the data
    response['Transfer-Encoding'] = 'chunked'
    print("finished in create_stream")
    print(response)
    return response
