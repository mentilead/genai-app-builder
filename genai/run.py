import environ
import os
import argparse

from providers import bedrock, openai


def main(args):
    # your 'launch code' goes here

    env = environ.Env(
        # set casting, default value
        DEBUG=(bool, False)
    )

    environ.Env.read_env(os.path.join('../.env'))

    if args.provider == 'openai':
        MAX_TOKENS = 10
        TEMPERATURE = 0.5

        model_parameters = {'max_tokens': MAX_TOKENS,
                            "temperature": TEMPERATURE
                            }

        client = openai.OpenAIClientManager(env('OPENAI_API_KEY'), model_id="gpt-3.5-turbo",
                                            model_kwargs=model_parameters)
        response = client.textgen_llm.stream(input="Write a 200 word text about Denmark")
        for chunk in response:
            print(chunk.content, end="", flush=True)

    elif args.provider == "anthropic":
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

        response = client.textgen_llm.stream(input="Human: Write a 20 word text about Denmark Assistant:")
        for chunk in response:
            print(chunk, end="", flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is my program description")
    parser.add_argument('-p', '--provider', type=str, required=True, help='Model provider')

    args = parser.parse_args()
    main(args)
