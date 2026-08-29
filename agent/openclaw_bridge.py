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
    try:
        response = requests.post(GATEWAY_URL, headers=headers, json=payload, timeout=30)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"OpenClaw connection failed: {e}"}

def delegate_task(instruction, agent_id="main"):
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
    try:
        response = requests.post(CHAT_URL, headers=headers, json=payload, timeout=150)
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "OpenClaw took too long to respond and timed out. The task may have partially completed — check manually if needed."
    except requests.exceptions.RequestException as e:
        return f"OpenClaw connection error: {e}"
    except (KeyError, ValueError):
        return f"Error: unexpected response format ({response.status_code} - {response.text[:200]})"
