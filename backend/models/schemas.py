from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    tools_used: Optional[List[str]] = None
    movies: Optional[List[Dict[str, Any]]] = None

class MovieSearchRequest(BaseModel):
    query: str
    page: Optional[int] = 1

class MovieDetailsRequest(BaseModel):
    movie_id: int

class RecommendationRequest(BaseModel):
    movie_title: str
    limit: Optional[int] = 5

class WatchOrderRequest(BaseModel):
    collection_name: str

class MovieCollection(BaseModel):
    id: int
    name: str
    overview: Optional[str]
    poster_path: Optional[str]
    backdrop_path: Optional[str]
    movies: List[Dict[str, Any]]

class MovieDetail(BaseModel):
    id: int
    title: str
    overview: Optional[str]
    release_date: Optional[str]
    runtime: Optional[int]
    vote_average: Optional[float]
    vote_count: Optional[int]
    poster_path: Optional[str]
    backdrop_path: Optional[str]
    genres: List[str]
    cast: Optional[List[Dict[str, Any]]]
    director: Optional[str]
    collection: Optional[Dict[str, Any]]
    similar_movies: Optional[List[Dict[str, Any]]]

class MemoryContext(BaseModel):
    conversation_id: str
    messages: List[ChatMessage]
    favorite_genres: Optional[List[str]] = []
    favorite_actors: Optional[List[str]] = []
    watched_movies: Optional[List[str]] = []
    last_recommendation: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = {}

class ToolCall(BaseModel):
    tool_name: str
    input: Dict[str, Any]
    output: Optional[Any] = None
    timestamp: Optional[datetime] = None