from agent.llm_client import LLMClient

DELEGATE_PROMPT = """Classify this request as either DIRECT or DELEGATE.

DIRECT = Mitchell can answer this through conversation or research/reasoning alone
(questions, advice, research, casual chat, hackathon validation, scheduling talk).

DELEGATE = this requires actually DOING something on the computer — creating,
reading, or modifying real files, running commands, checking system state, or
any action that needs real execution rather than just an answer.

Request: "{message}"

Respond with exactly one word: DIRECT or DELEGATE
"""

router = LLMClient(model="qwen3:1.7b")

def should_delegate(message):
    messages = [{"role": "user", "content": DELEGATE_PROMPT.format(message=message)}]
    response = router.chat(messages)
    result = response["message"]["content"].strip().upper()
    return "DELEGATE" in result
