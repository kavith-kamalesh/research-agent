import requests

class LLMClient:
    def __init__(self, model="qwen3:1.7b", host="http://localhost:11434"):
        self.model = model
        self.host = host

    def chat(self, messages, tools=None):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_ctx": 4096,
                "num_predict": 2000,
                "temperature": 0.3
            }
        }
        if tools:
            payload["tools"] = tools
        r = requests.post(f"{self.host}/api/chat", json=payload)
        return r.json()
