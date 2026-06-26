import httpx
from typing import Optional, List, Dict, Any
from config import Config

class TMDBClient:
    def __init__(self):
        self.api_key = Config.TMDB_API_KEY
        self.base_url = Config.TMDB_BASE_URL
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search_movies(self, query: str, page: int = 1) -> Dict[str, Any]:
        """Search for movies by title"""
        url = f"{self.base_url}/search/movie"
        params = {
            "api_key": self.api_key,
            "query": query,
            "page": page
        }
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def search_tv_shows(self, query: str, page: int = 1) -> Dict[str, Any]:
        """Search for TV shows by title"""
        url = f"{self.base_url}/search/tv"
        params = {
            "api_key": self.api_key,
            "query": query,
            "page": page
        }
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """Get detailed information about a movie"""
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            "api_key": self.api_key,
            "append_to_response": "credits,similar,images"
        }
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_movie_credits(self, movie_id: int) -> Dict[str, Any]:
        """Get cast and crew information for a movie"""
        url = f"{self.base_url}/movie/{movie_id}/credits"
        params = {"api_key": self.api_key}
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_similar_movies(self, movie_id: int, page: int = 1) -> Dict[str, Any]:
        """Get similar movies"""
        url = f"{self.base_url}/movie/{movie_id}/similar"
        params = {
            "api_key": self.api_key,
            "page": page
        }
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_collection_details(self, collection_id: int) -> Dict[str, Any]:
        """Get collection details including all movies in the collection"""
        url = f"{self.base_url}/collection/{collection_id}"
        params = {"api_key": self.api_key}
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_discover_movies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Discover movies by various criteria"""
        url = f"{self.base_url}/discover/movie"
        params["api_key"] = self.api_key
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_genres(self) -> Dict[str, Any]:
        """Get list of movie genres"""
        url = f"{self.base_url}/genre/movie/list"
        params = {"api_key": self.api_key}
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_movie_videos(self, movie_id: int) -> Dict[str, Any]:
        """Get trailers and videos for a movie"""
        url = f"{self.base_url}/movie/{movie_id}/videos"
        params = {"api_key": self.api_key}
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_trending_movies(self, time_window: str = "week") -> Dict[str, Any]:
        """Get trending movies"""
        url = f"{self.base_url}/trending/movie/{time_window}"
        params = {"api_key": self.api_key}
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()