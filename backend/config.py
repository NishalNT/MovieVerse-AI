import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    TMDB_BASE_URL = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    COHERE_BASE_URL = os.getenv("COHERE_BASE_URL", "https://api.cohere.ai/v1")
    
    @classmethod
    def validate(cls):
        if not cls.COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY is required")
        if not cls.TMDB_API_KEY:
            raise ValueError("TMDB_API_KEY is required")