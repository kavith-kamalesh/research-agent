import arxiv

def search_papers(query, max_results=5):
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
    results = []
    for r in search.results():
        results.append({
            "title": r.title,
            "summary": r.summary[:300],
            "url": r.entry_id,
            "published": str(r.published)
        })
    return results

PAPER_TOOL = {
    "type": "function",
    "function": {
        "name": "search_papers",
        "description": "Search arXiv for relevant academic papers and published research",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    }
}
