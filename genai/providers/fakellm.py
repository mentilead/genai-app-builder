from langchain.llms.fake import FakeStreamingListLLM

fakeLLM = FakeStreamingListLLM(responses=["this is a test"], sleep=0.05)
response = fakeLLM.stream()
for chunk in response:
    print(chunk, end="", flush=True)
