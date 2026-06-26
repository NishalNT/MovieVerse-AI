import httpx
from typing import Optional, List, Dict, Any
from config import Config

class CohereClient:
    def __init__(self):
        self.api_key = Config.COHERE_API_KEY
        self.base_url = Config.COHERE_BASE_URL
        self.client = httpx.AsyncClient(timeout=60.0)
        self.model = "command-a-03-2025"

    async def chat(self, 
                   message: str,
                   chat_history: Optional[List[Dict[str, str]]] = None,
                   tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Send a chat message to Cohere"""
        url = f"{self.base_url}/chat"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "message": message,
            "chat_history": chat_history or [],
            "tools": tools or []
        }
        
        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    async def generate_recommendation(self, 
                                      context: str,
                                      movie_data: List[Dict[str, Any]]) -> str:
        """Generate a recommendation based on movie data"""
        url = f"{self.base_url}/generate"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""You are a professional movie expert. Based on the following context and movie data, provide a personalized recommendation.
        Context: {context}
        Movie Data:
        {movie_data}
        Provide a detailed recommendation explaining why these movies would be good choices, considering the user's preferences and the movies' qualities."""
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("generations", [{}])[0].get("text", "")

    async def explain_watch_order(self, 
                                  collection_name: str,
                                  movies: List[Dict[str, Any]],
                                  order_type: str = "release") -> str:
        """Generate an explanation for the watch order"""
        url = f"{self.base_url}/generate"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""As a movie expert, explain the watch order for the {collection_name} collection.

Movies in {order_type} order:
{movies}

Provide a clear explanation of why this order is recommended, including:
1. The chronological order of events
2. The release order
3. Any important context for viewing
4. Special considerations for first-time viewers"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": 400,
            "temperature": 0.5
        }
        
        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("generations", [{}])[0].get("text", "")

    async def close(self):
        await self.client.aclose()