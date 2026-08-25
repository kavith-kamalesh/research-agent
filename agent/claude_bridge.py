from agent.llm_client import LLMClient

REFINE_PROMPT = """Refine this research report into exactly this format:

TIGHTENED SUMMARY: [3-5 lines max, the core takeaway]
ACTION PROMPT: [a single, ready-to-paste prompt someone could use elsewhere to act on this]
RISKS/GAPS: [anything uncertain or unresolved worth flagging before acting]

Report:
{report}
"""

refiner = LLMClient(model="qwen3:1.7b")

def refine_with_claude(report_text):
    messages = [{"role": "user", "content": REFINE_PROMPT.format(report=report_text)}]
    response = refiner.chat(messages)
    return response["message"]["content"]
