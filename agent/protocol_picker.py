from agent.llm_client import LLMClient

PICKER_PROMPT = """A user has given you this problem to research:

"{problem}"

Based on the nature of this problem, recommend ONE protocol and explain in
1-2 sentences why it fits. Choose from:

P1 Scientific Method — for testable/empirical questions
P2 First Principles — for engineering/design questions
P3 Mathematical Modeling — for quantitative/optimization questions
P4 Physics Heuristics — for fast feasibility/sanity checks
P5 Full JARVIS Report — for open-ended "should I build this" problems needing
   a complete investigation (problem definition, research, solution space,
   architecture, feasibility, cost, failure analysis, prototype plan, and
   verdict)

Respond in this exact format:
RECOMMENDED: [P#]
REASON: [1-2 sentences]
"""

picker = LLMClient(model="qwen3:1.7b")

def suggest_protocol(problem_text):
    messages = [{"role": "user", "content": PICKER_PROMPT.format(problem=problem_text)}]
    response = picker.chat(messages)
    return response["message"]["content"]
