import requests
import os

class LLMClient:
    def __init__(self, model="qwen3:1.7b", host="http://localhost:11434", backend="ollama"):
        self.model = model
        self.host = host
        self.backend = backend
        if backend == "groq":
            from groq import Groq
            self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def chat(self, messages, tools=None):
        if self.backend == "groq":
            return self._chat_groq(messages, tools)
        return self._chat_ollama(messages, tools)

    def _chat_ollama(self, messages, tools=None):
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

    def _chat_groq(self, messages, tools=None):
        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
        response = self.groq_client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        return {
            "message": {
                "content": choice.message.content or "",
                "tool_calls": getattr(choice.message, "tool_calls", None)
            }
        }
