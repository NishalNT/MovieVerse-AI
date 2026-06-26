from typing import Dict, Any, List, Optional
from services.tmdb_client import TMDBClient
import json
from logger import logger

class AgentTools:
    def __init__(self):
        self.tmdb_client = TMDBClient()

    async def search_movie(self, movie_title: str) -> Dict[str, Any]:
        """Search for movies by title"""
        try:
            results = await self.tmdb_client.search_movies(movie_title)
            
            # Format results with full movie data
            movies = []
            for movie in results.get("results", [])[:10]:
                movies.append({
                    "id": movie.get("id"),
                    "title": movie.get("title"),
                    "release_date": movie.get("release_date"),
                    "vote_average": movie.get("vote_average"),
                    "vote_count": movie.get("vote_count"),
                    "overview": movie.get("overview"),
                    "poster_path": movie.get("poster_path"),
                    "backdrop_path": movie.get("backdrop_path"),
                    "genre_ids": movie.get("genre_ids", []),
                    "popularity": movie.get("popularity"),
                    "original_language": movie.get("original_language")
                })
            
            return {
                "tool_name": "search_movie",
                "results": movies,
                "total_results": results.get("total_results", 0),
                "query": movie_title
            }
        except Exception as e:
            return {
                "tool_name": "search_movie",
                "error": str(e),
                "query": movie_title
            }

    async def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific movie"""
        try:
            details = await self.tmdb_client.get_movie_details(movie_id)
            credits = await self.tmdb_client.get_movie_credits(movie_id)
            
            # Get genres as list of strings
            genres = [g.get("name") for g in details.get("genres", [])]
            
            # Get cast (top 10)
            cast = []
            if credits and "cast" in credits:
                for actor in credits.get("cast", [])[:10]:
                    cast.append({
                        "name": actor.get("name"),
                        "character": actor.get("character"),
                        "profile_path": actor.get("profile_path")
                    })
            
            # Get director
            director = None
            if credits and "crew" in credits:
                for crew_member in credits.get("crew", []):
                    if crew_member.get("job") == "Director":
                        director = crew_member.get("name")
                        break
            
            movie_data = {
                "id": details.get("id"),
                "title": details.get("title"),
                "overview": details.get("overview"),
                "release_date": details.get("release_date"),
                "runtime": details.get("runtime"),
                "vote_average": details.get("vote_average"),
                "vote_count": details.get("vote_count"),
                "poster_path": details.get("poster_path"),
                "backdrop_path": details.get("backdrop_path"),
                "genres": genres,
                "cast": cast,
                "director": director,
                "tagline": details.get("tagline"),
                "status": details.get("status"),
                "budget": details.get("budget"),
                "revenue": details.get("revenue"),
                "collection": details.get("belongs_to_collection")
            }
            
            return {
                "tool_name": "get_movie_details",
                "results": movie_data
            }
        except Exception as e:
            return {
                "tool_name": "get_movie_details",
                "error": str(e),
                "movie_id": movie_id
            }
            
    async def search_collection(self, collection_name: str) -> Dict[str, Any]:
        """Search for a movie collection/series"""
        logger.info(f"Searching for collection: {collection_name}")
        
        try:
            # Clean the collection name
            collection_name = collection_name.strip()
            logger.debug(f"Cleaned collection name: {collection_name}")
            
            # Search for movies with this name
            logger.debug("Searching TMDB for movies...")
            search_results = await self.tmdb_client.search_movies(collection_name)
            logger.debug(f"Search results: {len(search_results.get('results', []))} movies found")
            
            # Find collections in results
            collections = []
            for movie in search_results.get("results", []):
                if movie.get("belongs_to_collection"):
                    collection = movie.get("belongs_to_collection")
                    if collection and collection not in collections:
                        collections.append(collection)
                        logger.debug(f"Found collection: {collection.get('name')} (ID: {collection.get('id')})")
            
            # If no collection found, try searching with variations
            if not collections:
                logger.warning(f"No collection found for '{collection_name}', trying variations...")
                variations = [
                    collection_name,
                    f"{collection_name} series",
                    f"{collection_name} collection",
                    f"The {collection_name}",
                    f"{collection_name} franchise"
                ]
                
                for variation in variations:
                    if variation != collection_name:
                        logger.debug(f"Trying variation: {variation}")
                        search_results = await self.tmdb_client.search_movies(variation)
                        for movie in search_results.get("results", []):
                            if movie.get("belongs_to_collection"):
                                collection = movie.get("belongs_to_collection")
                                if collection and collection not in collections:
                                    collections.append(collection)
                                    logger.debug(f"Found collection from variation: {collection.get('name')}")
                        if collections:
                            break
            
            if collections:
                collection_id = collections[0].get("id")
                logger.info(f"Found collection: {collections[0].get('name')} (ID: {collection_id})")
                
                if collection_id:
                    collection_details = await self.tmdb_client.get_collection_details(collection_id)
                    logger.debug(f"Retrieved collection details with {len(collection_details.get('parts', []))} parts")
                    
                    movies = []
                    for movie in collection_details.get("parts", []):
                        movies.append({
                            "id": movie.get("id"),
                            "title": movie.get("title"),
                            "release_date": movie.get("release_date"),
                            "overview": movie.get("overview"),
                            "poster_path": movie.get("poster_path"),
                            "backdrop_path": movie.get("backdrop_path"),
                            "vote_average": movie.get("vote_average"),
                            "vote_count": movie.get("vote_count"),
                            "original_title": movie.get("original_title")
                        })
                    
                    # Sort by release date
                    movies_sorted = sorted(
                        movies, 
                        key=lambda x: x.get("release_date") or "0000-00-00"
                    )
                    
                    logger.info(f"Returning {len(movies_sorted)} movies from collection")
                    return {
                        "tool_name": "search_collection",
                        "results": {
                            "collection_id": collection_id,
                            "collection_name": collections[0].get("name"),
                            "collection_overview": collection_details.get("overview"),
                            "poster_path": collection_details.get("poster_path"),
                            "backdrop_path": collection_details.get("backdrop_path"),
                            "movie_count": len(movies_sorted),
                            "movies": movies_sorted
                        }
                    }
            
            logger.warning(f"No collection found for '{collection_name}'")
            return {
                "tool_name": "search_collection",
                "results": None,
                "message": f"No collection found for '{collection_name}'",
                "suggestion": "Try searching for a specific movie title or series name"
            }
        except Exception as e:
            logger.error(f"Error searching collection: {str(e)}", {
                "error": str(e),
                "collection_name": collection_name
            })
            return {
                "tool_name": "search_collection",
                "error": str(e),
                "collection_name": collection_name
            }
       
       
    async def get_recommendations(self, movie_title: str, limit: int = 5) -> Dict[str, Any]:
        """Get recommendations based on a movie"""
        try:
            # Search for the movie
            search_results = await self.tmdb_client.search_movies(movie_title)
            
            if not search_results.get("results"):
                return {
                    "tool_name": "get_recommendations",
                    "error": f"Movie '{movie_title}' not found",
                    "movie_title": movie_title
                }
            
            movie_id = search_results.get("results")[0].get("id")
            
            # Get similar movies
            similar = await self.tmdb_client.get_similar_movies(movie_id, 1)
            
            recommendations = []
            for movie in similar.get("results", [])[:limit]:
                recommendations.append({
                    "id": movie.get("id"),
                    "title": movie.get("title"),
                    "release_date": movie.get("release_date"),
                    "vote_average": movie.get("vote_average"),
                    "vote_count": movie.get("vote_count"),
                    "overview": movie.get("overview"),
                    "poster_path": movie.get("poster_path"),
                    "backdrop_path": movie.get("backdrop_path"),
                    "genre_ids": movie.get("genre_ids", [])
                })
            
            # Get the original movie details
            original_movie = search_results.get("results")[0]
            
            return {
                "tool_name": "get_recommendations",
                "results": {
                    "based_on": movie_title,
                    "based_on_id": movie_id,
                    "based_on_poster": original_movie.get("poster_path"),
                    "recommendations": recommendations
                }
            }
        except Exception as e:
            return {
                "tool_name": "get_recommendations",
                "error": str(e),
                "movie_title": movie_title
            }

    async def get_actor_movies(self, actor_name: str) -> Dict[str, Any]:
        """Get movies featuring a specific actor"""
        try:
            # Search for person
            url = f"https://api.themoviedb.org/3/search/person"
            params = {
                "api_key": self.tmdb_client.api_key,
                "query": actor_name
            }
            response = await self.tmdb_client.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("results"):
                return {
                    "tool_name": "get_actor_movies",
                    "error": f"Actor '{actor_name}' not found",
                    "actor_name": actor_name
                }
            
            person_id = data.get("results")[0].get("id")
            person_name = data.get("results")[0].get("name")
            
            # Get person's movie credits
            url = f"https://api.themoviedb.org/3/person/{person_id}/movie_credits"
            params = {"api_key": self.tmdb_client.api_key}
            response = await self.tmdb_client.client.get(url, params=params)
            response.raise_for_status()
            credits = response.json()
            
            movies = []
            for movie in credits.get("cast", [])[:10]:
                movies.append({
                    "id": movie.get("id"),
                    "title": movie.get("title"),
                    "release_date": movie.get("release_date"),
                    "vote_average": movie.get("vote_average"),
                    "vote_count": movie.get("vote_count"),
                    "character": movie.get("character"),
                    "poster_path": movie.get("poster_path"),
                    "backdrop_path": movie.get("backdrop_path"),
                    "overview": movie.get("overview")
                })
            
            return {
                "tool_name": "get_actor_movies",
                "results": {
                    "actor": person_name,
                    "actor_id": person_id,
                    "movie_count": len(movies),
                    "movies": movies
                }
            }
        except Exception as e:
            return {
                "tool_name": "get_actor_movies",
                "error": str(e),
                "actor_name": actor_name
            }
    async def get_watch_order(self, collection_name: str) -> Dict[str, Any]:
        """Get recommended watch order for a collection/series"""
        try:
            # Clean the collection name
            collection_name = collection_name.strip()
            
            # First find the collection
            collection_result = await self.search_collection(collection_name)
            
            if not collection_result.get("results"):
                # Try to search for movies with this name
                search_result = await self.search_movie(collection_name)
                if search_result.get("results"):
                    # Use the first movie to find its collection
                    first_movie = search_result["results"][0]
                    if first_movie.get("id"):
                        # Get movie details to find collection
                        movie_details = await self.get_movie_details(first_movie["id"])
                        if movie_details.get("results") and movie_details["results"].get("collection"):
                            collection = movie_details["results"]["collection"]
                            # Now get the full collection
                            collection_result = await self.search_collection(collection.get("name"))
                            if collection_result.get("results"):
                                collection_data = collection_result["results"]
                                movies = collection_data.get("movies", [])
                                if movies:
                                    release_order = sorted(
                                        movies, 
                                        key=lambda x: x.get("release_date") or "0000-00-00"
                                    )
                                    return {
                                        "tool_name": "get_watch_order",
                                        "results": {
                                            "collection_name": collection_data.get("collection_name"),
                                            "collection_id": collection_data.get("collection_id"),
                                            "movie_count": len(release_order),
                                            "release_order": release_order,
                                            "chronological_order": release_order,  # Same as release for now
                                            "suggested_order": "release",
                                            "reasoning": "Release order is generally recommended for first-time viewers to preserve the intended narrative experience and character development."
                                        }
                                    }
                
                return {
                    "tool_name": "get_watch_order",
                    "error": f"Collection '{collection_name}' not found",
                    "collection_name": collection_name,
                    "suggestion": "Try searching for a specific movie title or series name"
                }
            
            collection_data = collection_result["results"]
            movies = collection_data.get("movies", [])
            
            if not movies:
                return {
                    "tool_name": "get_watch_order",
                    "results": None,
                    "message": f"No movies found in collection '{collection_name}'"
                }
            
            # Sort by release date for release order
            release_order = sorted(
                movies, 
                key=lambda x: x.get("release_date") or "0000-00-00"
            )
            
            return {
                "tool_name": "get_watch_order",
                "results": {
                    "collection_name": collection_data.get("collection_name"),
                    "collection_id": collection_data.get("collection_id"),
                    "movie_count": len(release_order),
                    "release_order": release_order,
                    "chronological_order": release_order,
                    "suggested_order": "release",
                    "reasoning": "Release order is generally recommended for first-time viewers to preserve the intended narrative experience and character development."
                }
            }
        except Exception as e:
            return {
                "tool_name": "get_watch_order",
                "error": str(e),
                "collection_name": collection_name
            }
            
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools for the agent"""
        return [
            {
                "name": "search_movie",
                "description": "Search for movies by title",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "movie_title": {
                            "type": "string",
                            "description": "The title of the movie to search for"
                        }
                    },
                    "required": ["movie_title"]
                }
            },
            {
                "name": "get_movie_details",
                "description": "Get detailed information about a specific movie",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "movie_id": {
                            "type": "integer",
                            "description": "The TMDB ID of the movie"
                        }
                    },
                    "required": ["movie_id"]
                }
            },
            {
                "name": "search_collection",
                "description": "Search for a movie collection or series",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "The name of the collection"
                        }
                    },
                    "required": ["collection_name"]
                }
            },
            {
                "name": "get_recommendations",
                "description": "Get movie recommendations based on a movie",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "movie_title": {
                            "type": "string",
                            "description": "The title of the movie to base recommendations on"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of recommendations to return",
                            "default": 5
                        }
                    },
                    "required": ["movie_title"]
                }
            },
            {
                "name": "get_actor_movies",
                "description": "Get movies featuring a specific actor",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "actor_name": {
                            "type": "string",
                            "description": "The name of the actor"
                        }
                    },
                    "required": ["actor_name"]
                }
            },
            {
                "name": "get_watch_order",
                "description": "Get recommended watch order for a collection or series",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "The name of the collection or series"
                        }
                    },
                    "required": ["collection_name"]
                }
            }
        ]