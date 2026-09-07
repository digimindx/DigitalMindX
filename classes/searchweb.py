from ddgs import DDGS

# ==========================================
# 🔍 SEARCH MANAGER
# ==========================================
class SearchManager:
    """Handles all web search operations."""

    @staticmethod
    def web_search(lookingfor: str) -> str:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(lookingfor, max_results=5))
                if not results:
                    return "No results found for your query."
                
                formatted_results = []
                for r in results:
                    title = r.get('title', 'N/A')
                    url = r.get('href', 'N/A')
                    snippet = r.get('body', 'N/A')
                    formatted_results.append(f"Title: {title}\nURL: {url}\nSnippet: {snippet}")
                
                return "\n\n---\n\n".join(formatted_results)
        except Exception as e:
            return f"An error occurred during the web search: {str(e)}"

    @property
    def schemas(self) -> list:
        return [{
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web using DuckDuckGo for real-time information, facts, or news.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lookingfor": {"type": "string", "description": "The specific search query to look up on the web."}
                    },
                    "required": ["lookingfor"]
                }
            }
        }]

    @property
    def tools(self) -> dict:
        return {"web_search": self.web_search}
