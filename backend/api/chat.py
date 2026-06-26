from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from models.schemas import ChatRequest, ChatResponse, MessageRole
from agent.graph import AgentGraph
from memory.memory import MemoryManager
import uuid

router = APIRouter()
agent = AgentGraph()
memory = MemoryManager()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message"""
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get chat history from memory
        chat_history = memory.get_chat_history(conversation_id)
        
        # Process through agent
        result = await agent.process_message(
            message=request.message,
            conversation_id=conversation_id,
            chat_history=chat_history
        )
        
        # Store conversation in memory
        memory.add_message(conversation_id, MessageRole.USER, request.message)
        memory.add_message(conversation_id, MessageRole.ASSISTANT, result["response"])
        
        # Extract and format movies from result
        movies = result.get("movies", [])
        
        # Ensure movies have proper poster paths
        formatted_movies = []

        for movie in movies:
            if movie and isinstance(movie, dict):
                # Format movie data for frontend
                formatted_movie = {
                    "id": movie.get("id"),
                    "title": movie.get("title"),
                    "overview": movie.get("overview"),
                    "release_date": movie.get("release_date"),
                    "runtime": movie.get("runtime"),
                    "vote_average": movie.get("vote_average"),
                    "vote_count": movie.get("vote_count"),
                    "poster_path": movie.get("poster_path"),
                    "backdrop_path": movie.get("backdrop_path"),
                    "genres": movie.get("genres", []),
                    "cast": movie.get("cast", []),
                    "director": movie.get("director"),
                    "tagline": movie.get("tagline"),
                    "collection": movie.get("collection")
                }
                formatted_movies.append(formatted_movie)
        return ChatResponse(
            response=result["response"],
            conversation_id=conversation_id,
            tools_used=result.get("tools_used", []),
            movies=formatted_movies[:10]  # Limit to 10 movies
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    """Get chat history for a conversation"""
    try:
        history = memory.get_chat_history(conversation_id)
        return {"conversation_id": conversation_id, "messages": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/history/{conversation_id}")
async def clear_chat_history(conversation_id: str):
    """Clear chat history for a conversation"""
    try:
        memory.save_memory(memory.get_or_create_memory(conversation_id))
        return {"message": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))