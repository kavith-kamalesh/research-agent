from agent.llm_client import LLMClient
from agent.persona import CORE_IDENTITY
from agent.protocols import RESEARCH_PROTOCOLS
from agent.hackathon_mode import HACKATHON_PROTOCOL
from agent.tools.web_search import web_search, TOOLS
import json

client = LLMClient()

PROTOCOL_MAP = {
    "HACKATHON": HACKATHON_PROTOCOL,
}

def extract_protocol(user_input):
    if user_input.startswith("[Use protocol "):
        end = user_input.index("]")
        protocol_name = user_input[14:end].strip()
        clean_input = user_input[end+1:].strip()
        return protocol_name, clean_input
    return None, user_input

def run(user_input, history=None):
    protocol_name, clean_input = extract_protocol(user_input)

    use_tools = True

    if protocol_name and protocol_name in PROTOCOL_MAP:
        # Focused prompt: identity + ONLY the relevant protocol, no tools needed
        system_content = CORE_IDENTITY + "\n\n" + PROTOCOL_MAP[protocol_name] + f"\n\nIf the user gave you a real, specific idea to validate, you MUST use the {protocol_name} REPORT format above, with every section filled in — do not skip the scoring or structure. If the user did NOT give a specific idea (e.g. they asked a general question), do not use the report format at all — just answer their actual question directly and ask them to share their idea."
        messages = [{"role": "system", "content": system_content}]
        messages.append({"role": "user", "content": clean_input})
        use_tools = False
    else:
        # Default: full research protocols for VERITAS/GENESIS/AXIOM/SENTRY/ORACLE
        messages = history or [{"role": "system", "content": CORE_IDENTITY + "\n\n" + RESEARCH_PROTOCOLS}]
        messages.append({"role": "user", "content": user_input})

    response = client.chat(messages, tools=TOOLS if use_tools else None)
    msg = response["message"]

    if msg.get("tool_calls"):
        for call in msg["tool_calls"]:
            if call["function"]["name"] == "web_search":
                args = call["function"]["arguments"]
                result = web_search(args["query"])
                messages.append(msg)
                messages.append({"role": "tool", "content": json.dumps(result)})
        response = client.chat(messages)
        msg = response["message"]

    content_out = msg["content"]
    # Safety net: strip any leaked raw tool-call text the model emits as plain text
    import re
    content_out = re.sub(r"<tools?>.*?</tools?>", "", content_out, flags=re.DOTALL).strip()

    messages.append(msg)
    return content_out, messages
