from agent.llm_client import LLMClient

ROUTE_PROMPT = """Classify this message as either CASUAL or RESEARCH.

CASUAL = greetings, small talk, personal questions, scheduling, reminders,
general advice, or anything that doesn't need formal investigation.

RESEARCH = a technical problem, feasibility question, design question, or
"should I build this" type request that would benefit from structured
investigation.

Message: "{message}"

Respond with exactly one word: CASUAL or RESEARCH
"""

router = LLMClient(model="openai/gpt-oss-120b", backend="groq")

def classify_message(message):
    messages = [{"role": "user", "content": ROUTE_PROMPT.format(message=message)}]
    response = router.chat(messages)
    result = response["message"]["content"].strip().upper()
    return "RESEARCH" if "RESEARCH" in result else "CASUAL"
