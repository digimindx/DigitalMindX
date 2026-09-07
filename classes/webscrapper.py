import requests
from bs4 import BeautifulSoup

# ==========================================
# 🌐 WEB SCRAPER MANAGER
# ==========================================
class WebScraper:
    """
    Handles visiting URLs, extracting clean text content, 
    and passing it back to the agent for analysis.
    """

    def read_url(self, url: str, max_length: int = 6000) -> str:
        try:
            # Ensure URL has a protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Standard browser headers to avoid basic bot blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
            }
            
            # Fetch the webpage
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status() # Raise an exception for bad status codes (404, 500, etc.)
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove non-content elements that clutter the LLM's context
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'noscript', 'iframe']):
                element.decompose()
            
            # Extract clean text
            text = soup.get_text(separator='\n', strip=True)
            
            # Truncate if the content is too large to fit in the LLM's context window
            if len(text) > max_length:
                text = text[:max_length] + "\n\n---\n[⚠️ Content truncated due to length. Ask me to search for specific details if needed.]"
            
            return f"Successfully fetched and extracted content from: {url}\n\n{text}"
            
        except requests.exceptions.HTTPError as e:
            return f"HTTP Error fetching URL: {str(e)}"
        except requests.exceptions.ConnectionError:
            return f"Connection Error: Could not connect to '{url}'. Check if the URL is correct."
        except requests.exceptions.Timeout:
            return f"Timeout Error: The request to '{url}' took too long."
        except Exception as e:
            return f"An unexpected error occurred while scraping: {str(e)}"

    @property
    def schemas(self) -> list:
        return [{
            "type": "function",
            "function": {
                "name": "read_url",
                "description": "Visits a given URL, extracts the main readable text content, and returns it for analysis.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The full URL to visit and extract content from (e.g., 'https://example.com/article')."
                        }
                    },
                    "required": ["url"]
                }
            }
        }]

    @property
    def tools(self) -> dict:
        return {"read_url": self.read_url}