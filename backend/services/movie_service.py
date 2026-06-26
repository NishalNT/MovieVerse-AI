from typing import List, Dict, Any, Optional
from services.tmdb_client import TMDBClient

class MovieService:
    def __init__(self):
        self.tmdb_client = TMDBClient()

    async def search_movies(self, query: str, page: int = 1) -> Dict[str, Any]:
        """Search for movies"""
        return await self.tmdb_client.search_movies(query, page)

    async def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """Get movie details"""
        details = await self.tmdb_client.get_movie_details(movie_id)
        credits = await self.tmdb_client.get_movie_credits(movie_id)
        
        # Add credits to details
        details["credits"] = credits
        
        return details

    async def get_movie_recommendations(self, movie_id: int, limit: int = 5) -> Dict[str, Any]:
        """Get movie recommendations"""
        similar = await self.tmdb_client.get_similar_movies(movie_id)
        
        # Filter and limit results
        recommendations = similar.get("results", [])[:limit]
        
        return {
            "movie_id": movie_id,
            "recommendations": recommendations
        }

    async def get_collection_details(self, collection_id: int) -> Dict[str, Any]:
        """Get collection details"""
        return await self.tmdb_client.get_collection_details(collection_id)

    async def get_actor_movies(self, actor_name: str) -> Dict[str, Any]:
        """Get movies by actor"""
        # Search for actor
        url = f"https://api.themoviedb.org/3/search/person"
        params = {
            "api_key": self.tmdb_client.api_key,
            "query": actor_name
        }
        response = await self.tmdb_client.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("results"):
            return {"error": f"Actor '{actor_name}' not found"}
        
        person_id = data.get("results")[0].get("id")
        
        # Get actor's movies
        url = f"https://api.themoviedb.org/3/person/{person_id}/movie_credits"
        params = {"api_key": self.tmdb_client.api_key}
        response = await self.tmdb_client.client.get(url, params=params)
        response.raise_for_status()
        credits = response.json()
        
        # Format movies with poster paths
        movies = []
        for movie in credits.get("cast", [])[:10]:
            movies.append({
                "id": movie.get("id"),
                "title": movie.get("title"),
                "release_date": movie.get("release_date"),
                "vote_average": movie.get("vote_average"),
                "poster_path": movie.get("poster_path"),
                "backdrop_path": movie.get("backdrop_path"),
                "overview": movie.get("overview"),
                "character": movie.get("character")
            })
        
        return {
            "actor": data.get("results")[0].get("name"),
            "movies": movies
        }

    async def get_watch_order(self, collection_name: str) -> Dict[str, Any]:
        """Get recommended watch order for a collection"""
        # Search for collection
        collection_result = await self._find_collection(collection_name)
        
        if not collection_result:
            return {"error": f"Collection '{collection_name}' not found"}
        
        collection_id = collection_result.get("id")
        collection_details = await self.tmdb_client.get_collection_details(collection_id)
        
        # Sort by release date
        movies = collection_details.get("parts", [])
        release_order = sorted(movies, key=lambda x: x.get("release_date") or "")
        
        return {
            "collection": collection_details.get("name"),
            "release_order": release_order,
            "suggested_order": "release",
            "reasoning": "Release order is recommended for first-time viewers to maintain the intended narrative flow."
        }

    async def _find_collection(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a collection by name"""
        search_results = await self.tmdb_client.search_movies(name)
        
        for movie in search_results.get("results", []):
            if movie.get("belongs_to_collection"):
                return movie.get("belongs_to_collection")
        
        return None