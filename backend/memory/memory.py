from typing import Optional, List, Dict, Any
from datetime import datetime
from models.schemas import ChatMessage, MemoryContext, MessageRole
import json
import os

class MemoryManager:
    def __init__(self, storage_dir: str = "./memory_storage"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.memories: Dict[str, MemoryContext] = {}

    def get_memory_path(self, conversation_id: str) -> str:
        return os.path.join(self.storage_dir, f"{conversation_id}.json")

    def load_memory(self, conversation_id: str) -> Optional[MemoryContext]:
        """Load conversation memory from storage"""
        path = self.get_memory_path(conversation_id)
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    return MemoryContext(**data)
            except Exception as e:
                print(f"Error loading memory: {e}")
                return None
        return None

    def save_memory(self, memory: MemoryContext) -> None:
        """Save conversation memory to storage"""
        path = self.get_memory_path(memory.conversation_id)
        try:
            with open(path, 'w') as f:
                json.dump(memory.dict(), f, default=str)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def get_or_create_memory(self, conversation_id: str) -> MemoryContext:
        """Get existing memory or create new one"""
        memory = self.load_memory(conversation_id)
        if not memory:
            memory = MemoryContext(
                conversation_id=conversation_id,
                messages=[]
            )
            self.save_memory(memory)
        return memory

    def add_message(self, 
                    conversation_id: str, 
                    role: MessageRole, 
                    content: str) -> MemoryContext:
        """Add a message to conversation memory"""
        memory = self.get_or_create_memory(conversation_id)
        
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        
        memory.messages.append(message)
        
        # Keep only last 50 messages to prevent context explosion
        if len(memory.messages) > 50:
            memory.messages = memory.messages[-50:]
        
        self.save_memory(memory)
        return memory

    def update_preferences(self, 
                          conversation_id: str, 
                          preferences: Dict[str, Any]) -> MemoryContext:
        """Update user preferences in memory"""
        memory = self.get_or_create_memory(conversation_id)
        memory.preferences.update(preferences)
        self.save_memory(memory)
        return memory

    def add_watched_movie(self, conversation_id: str, movie_title: str) -> MemoryContext:
        """Add a movie to watched list"""
        memory = self.get_or_create_memory(conversation_id)
        if movie_title not in memory.watched_movies:
            memory.watched_movies.append(movie_title)
        self.save_memory(memory)
        return memory

    def add_favorite_genre(self, conversation_id: str, genre: str) -> MemoryContext:
        """Add a genre to favorites"""
        memory = self.get_or_create_memory(conversation_id)
        if genre not in memory.favorite_genres:
            memory.favorite_genres.append(genre)
        self.save_memory(memory)
        return memory

    def add_favorite_actor(self, conversation_id: str, actor: str) -> MemoryContext:
        """Add an actor to favorites"""
        memory = self.get_or_create_memory(conversation_id)
        if actor not in memory.favorite_actors:
            memory.favorite_actors.append(actor)
        self.save_memory(memory)
        return memory

    def get_last_recommendation(self, conversation_id: str) -> Optional[str]:
        """Get the last recommendation made"""
        memory = self.load_memory(conversation_id)
        if memory:
            return memory.last_recommendation
        return None

    def set_last_recommendation(self, conversation_id: str, recommendation: str) -> None:
        """Set the last recommendation"""
        memory = self.get_or_create_memory(conversation_id)
        memory.last_recommendation = recommendation
        self.save_memory(memory)

    def get_chat_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get chat history formatted for LLM"""
        memory = self.load_memory(conversation_id)
        if not memory:
            return []
        
        history = []
        for msg in memory.messages:
            history.append({
                "role": msg.role.value,
                "content": msg.content
            })
        return history