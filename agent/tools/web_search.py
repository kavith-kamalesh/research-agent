from ddgs import DDGS

def web_search(query: str, max_results=5):
    with DDGS() as ddgs:
        return [r for r in ddgs.text(query, max_results=max_results)]

TOOLS = [{
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for current information",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    }
}]
