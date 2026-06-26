export interface Movie {
  id: number;
  title: string;
  overview?: string;
  release_date?: string;
  runtime?: number;
  vote_average?: number;
  vote_count?: number;
  poster_path?: string;
  backdrop_path?: string;
  genres?: string[];
  cast?: Array<{ name: string; character: string; profile_path?: string }>;
  director?: string;
  collection?: {
    id: number;
    name: string;
    poster_path?: string;
    backdrop_path?: string;
  };
  tagline?: string;
  status?: string;
}

export interface MovieCollection {
  id: number;
  name: string;
  overview?: string;
  poster_path?: string;
  backdrop_path?: string;
  movies: Movie[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  movies?: Movie[];
  tools_used?: string[];
  isTyping?: boolean;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  user_id?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  tools_used?: string[];
  movies?: Movie[];
}

export interface MemoryContext {
  conversation_id: string;
  messages: ChatMessage[];
  favorite_genres: string[];
  favorite_actors: string[];
  watched_movies: string[];
  last_recommendation?: string;
  preferences: Record<string, any>;
}