from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.movie_service import MovieService
from services.tmdb_client import TMDBClient

router = APIRouter()
movie_service = MovieService()
tmdb_client = TMDBClient()

@router.get("/search")
async def search_movies(query: str = Query(..., min_length=1), page: int = 1):
    """Search for movies"""
    try:
        results = await movie_service.search_movies(query, page)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/details/{movie_id}")
async def get_movie_details(movie_id: int):
    """Get movie details"""
    try:
        details = await movie_service.get_movie_details(movie_id)
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/{movie_id}")
async def get_movie_recommendations(movie_id: int, limit: int = 5):
    """Get movie recommendations"""
    try:
        recommendations = await movie_service.get_movie_recommendations(movie_id, limit)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collection/{collection_id}")
async def get_collection_details(collection_id: int):
    """Get collection details"""
    try:
        collection = await movie_service.get_collection_details(collection_id)
        return collection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/actor/{actor_name}")
async def get_actor_movies(actor_name: str):
    """Get movies by actor"""
    try:
        actor_movies = await movie_service.get_actor_movies(actor_name)
        return actor_movies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/watch-order")
async def get_watch_order(collection_name: str = Query(..., min_length=1)):
    """Get watch order for a collection"""
    try:
        watch_order = await movie_service.get_watch_order(collection_name)
        return watch_order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trending")
async def get_trending_movies(time_window: str = "week"):
    """Get trending movies"""
    try:
        trending = await tmdb_client.get_trending_movies(time_window)
        return trending
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/genres")
async def get_genres():
    """Get movie genres"""
    try:
        genres = await tmdb_client.get_genres()
        return genres
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))