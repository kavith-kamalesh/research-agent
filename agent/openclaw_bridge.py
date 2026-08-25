import requests
import os

GATEWAY_URL = "http://127.0.0.1:18789/tools/invoke"
CHAT_URL = "http://127.0.0.1:18789/v1/chat/completions"
GATEWAY_TOKEN = os.getenv("OPENCLAW_TOKEN", "")

def invoke_tool(tool_name, args=None):
    headers = {
        "Authorization": f"Bearer {GATEWAY_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "tool": tool_name,
        "action": "json",
        "args": args or {}
    }
    response = requests.post(GATEWAY_URL, headers=headers, json=payload)
    return response.json()

def delegate_task(instruction, agent_id="main"):
    """Send a task instruction to OpenClaw's agent to actually execute."""
    headers = {
        "Authorization": f"Bearer {GATEWAY_TOKEN}",
        "Content-Type": "application/json",
        "x-openclaw-agent-id": agent_id
    }
    payload = {
        "model": "openclaw",
        "messages": [
            {"role": "user", "content": instruction}
        ]
    }
    response = requests.post(CHAT_URL, headers=headers, json=payload, timeout=120)
    try:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except (KeyError, ValueError):
        return f"Error: {response.status_code} - {response.text}"
