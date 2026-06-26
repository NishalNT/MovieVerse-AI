from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from api import chat, movie
from config import Config

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Config.validate()
    print("MovieVerse AI Backend started successfully!")
    yield
    # Shutdown
    print("Shutting down MovieVerse AI Backend...")

app = FastAPI(
    title="MovieVerse AI",
    description="Agentic AI Movie Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(movie.router, prefix="/api/movie", tags=["movie"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to MovieVerse AI API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "movie_search": "/api/movie/search",
            "movie_details": "/api/movie/details/{movie_id}",
            "recommendations": "/api/movie/recommendations/{movie_id}",
            "collection": "/api/movie/collection/{collection_id}",
            "actor": "/api/movie/actor/{actor_name}",
            "watch_order": "/api/movie/watch-order",
            "trending": "/api/movie/trending",
            "genres": "/api/movie/genres"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )   