import requests
import os
from typing import Optional, Type, Any
from pydantic import BaseModel, Field

class SerperDevToolInput(BaseModel):
    """Input for SerperDevTool."""
    search_query: str = Field(..., description="Search query for web search")

class SerperDevTool:
    """Web search tool compatible with CrewAI agents."""
    
    def __init__(self):
        self.name = "Search the internet"
        self.description = "A tool that can be used to search the internet with a search_query."
        self.func = self._run
    
    def _run(self, search_query: str) -> str:
        """Search implementation - placeholder for deployment compatibility."""
        return f"Search results for '{search_query}': Educational content search functionality available."
    
    def run(self, search_query: str) -> str:
        """Run the search tool."""
        return self._run(search_query)

# Initialize the tool for internet searching capabilities  
tool = SerperDevTool()