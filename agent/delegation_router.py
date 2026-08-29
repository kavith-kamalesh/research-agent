from agent.llm_client import LLMClient

DELEGATE_PROMPT = """Classify this request as either DIRECT or DELEGATE.

DELEGATE = the user is explicitly asking to DO something concrete on the
computer right now: create/write/edit/delete a real file, run a command,
check actual system state (disk space, processes), or a similarly concrete
action verb aimed at THIS machine.

DIRECT = everything else, including feasibility questions, "is it possible
to...", "how would I...", research questions, technical analysis, hackathon
validation, casual chat, or any question seeking an answer/opinion rather than
an action. When in doubt, choose DIRECT — only choose DELEGATE if the request
unambiguously asks for a real action to be performed right now.

Request: "{message}"

Respond with exactly one word: DIRECT or DELEGATE
"""

router = LLMClient(model="openai/gpt-oss-120b", backend="groq")

def should_delegate(message):
    messages = [{"role": "user", "content": DELEGATE_PROMPT.format(message=message)}]
    response = router.chat(messages)
    result = response["message"]["content"].strip().upper()
    return "DELEGATE" in result and "DIRECT" not in result
