import os
import requests
from typing import Optional, Type, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class SerperSearchInput(BaseModel):
    """Input schema for Serper search tool."""
    search_query: str = Field(..., description="The search query to search for")

class SerperDevTool(BaseTool):
    """Custom search tool using Serper API."""
    
    name: str = "search_internet"
    description: str = "A tool that can be used to search the internet with a search query. Useful for finding current information about sex education topics, health resources, and educational content."
    args_schema: Type[BaseModel] = SerperSearchInput
    
    def _run(self, search_query: str) -> str:
        """Execute the search using Serper API or fallback."""
        api_key = os.getenv("SERPER_API_KEY")
        
        if not api_key:
            # Fallback response when no API key is available
            return f"Search functionality for '{search_query}' is currently limited. For sex education topics, I recommend consulting official health resources like WHO, CDC, or certified medical professionals."
        
        try:
            url = "https://google.serper.dev/search"
            payload = {
                "q": search_query,
                "num": 5
            }
            headers = {
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            
            # Format search results
            if "organic" in results:
                formatted_results = []
                for result in results["organic"][:3]:  # Top 3 results
                    formatted_results.append(f"Title: {result.get('title', 'N/A')}\nSnippet: {result.get('snippet', 'N/A')}\nURL: {result.get('link', 'N/A')}\n")
                
                return f"Search results for '{search_query}':\n\n" + "\n".join(formatted_results)
            else:
                return f"No search results found for '{search_query}'. Please try a different search term."
                
        except requests.exceptions.RequestException as e:
            return f"Search temporarily unavailable for '{search_query}'. Error: {str(e)}"
        except Exception as e:
            return f"Search error for '{search_query}': {str(e)}"

# Create the tool instance
tool = SerperDevTool()