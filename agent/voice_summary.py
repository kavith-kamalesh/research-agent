
from agent.llm_client import LLMClient



SUMMARY_PROMPT = """Summarize this in ONE short spoken sentence, casual and natural,

as if telling a friend the headline. No markdown, no scores, just the gist.



Content: {content}

"""



summarizer = LLMClient(model="openai/gpt-oss-120b", backend="groq")



def get_spoken_summary(content):

    messages = [{"role": "user", "content": SUMMARY_PROMPT.format(content=content[:1000])}]

    response = summarizer.chat(messages)

    return response["message"]["content"]

