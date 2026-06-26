"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Menu,
  Plus,
  Sparkles,
  Send,
  Loader2,
  Film,
  Star,
  TrendingUp,
  Clock,
  Calendar,
  X,
  User,
  Clapperboard,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { chatAPI } from "@/services/api";
import { ChatMessage, Movie } from "@/types";
import Sidebar from "./Sidebar";
import Image from "next/image";

interface ChatProps {
  conversationId?: string;
}

// ─── localStorage helpers for movie cache ──────────────────────────────────────
// Key: conversationId → array of { contentSnippet: string; movies: Movie[] }
// We match by a 120-char snippet of the assistant message content (safe & fast).

const MOVIE_CACHE_KEY = "mv_movie_cache";

function saveMoviesToCache(convId: string, content: string, movies: Movie[]) {
  try {
    const raw = localStorage.getItem(MOVIE_CACHE_KEY);
    const cache: Record<string, { snippet: string; movies: Movie[] }[]> = raw
      ? JSON.parse(raw)
      : {};
    if (!cache[convId]) cache[convId] = [];
    const snippet = content.slice(0, 120);
    // Avoid duplicates
    const exists = cache[convId].some((e) => e.snippet === snippet);
    if (!exists) cache[convId].push({ snippet, movies });
    localStorage.setItem(MOVIE_CACHE_KEY, JSON.stringify(cache));
  } catch {
    // localStorage full or unavailable — silently skip
  }
}

function getMoviesFromCache(convId: string, content: string): Movie[] {
  try {
    const raw = localStorage.getItem(MOVIE_CACHE_KEY);
    if (!raw) return [];
    const cache: Record<string, { snippet: string; movies: Movie[] }[]> =
      JSON.parse(raw);
    const entries = cache[convId] || [];
    const snippet = content.slice(0, 120);
    const match = entries.find((e) => e.snippet === snippet);
    return match?.movies || [];
  } catch {
    return [];
  }
}

// ─── Star Rating ───────────────────────────────────────────────────────────────
const StarRating = ({ rating }: { rating: number }) => {
  const filled = Math.round(rating / 2);
  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((i) => (
        <Star
          key={i}
          className={`w-3 h-3 ${
            i <= filled ? "text-yellow-400 fill-yellow-400" : "text-white/20"
          }`}
        />
      ))}
      <span className="text-xs text-white/50 ml-1">{rating.toFixed(1)}</span>
    </div>
  );
};

// ─── Single Movie Card ─────────────────────────────────────────────────────────
const MovieCard = ({
  movie,
  onClick,
}: {
  movie: Movie;
  onClick: (movie: Movie) => void;
}) => {
  const [imgError, setImgError] = useState(false);
  const posterUrl = movie.poster_path
    ? `https://image.tmdb.org/t/p/w342${movie.poster_path}`
    : null;
  const year = movie.release_date
    ? new Date(movie.release_date).getFullYear()
    : null;

  return (
    <div
      onClick={() => onClick(movie)}
      className="group flex gap-3 p-3 rounded-xl cursor-pointer transition-all duration-200 hover:bg-white/5 border border-transparent hover:border-white/10"
    >
      {/* Poster */}
      <div
        className="shrink-0 rounded-lg overflow-hidden bg-white/5"
        style={{ width: 64, height: 96 }}
      >
        {posterUrl && !imgError ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={posterUrl}
            alt={movie.title}
            onError={() => setImgError(true)}
            style={{
              width: 64,
              height: 96,
              objectFit: "cover",
              display: "block",
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Film className="w-6 h-6 text-white/20" />
          </div>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0 space-y-1.5">
        <div>
          <p className="text-sm font-semibold text-white leading-tight group-hover:text-purple-300 transition-colors line-clamp-2">
            {movie.title}
          </p>
          {year && (
            <p className="text-xs text-white/40 mt-0.5 flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {year}
            </p>
          )}
        </div>

        {movie.vote_average ? <StarRating rating={movie.vote_average} /> : null}

        {movie.genres && movie.genres.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {movie.genres.slice(0, 2).map((g) => (
              <span
                key={g}
                className="text-[10px] px-1.5 py-0.5 bg-purple-500/20 text-purple-300 rounded-full border border-purple-500/20"
              >
                {g}
              </span>
            ))}
          </div>
        )}

        {movie.director && (
          <p className="text-xs text-white/40 flex items-center gap-1 truncate">
            <Clapperboard className="w-3 h-3 shrink-0" />
            {movie.director}
          </p>
        )}

        {movie.cast && movie.cast.length > 0 && (
          <p className="text-xs text-white/35 flex items-center gap-1 truncate">
            <User className="w-3 h-3 shrink-0" />
            {movie.cast
              .slice(0, 2)
              .map((a) => a.name)
              .join(", ")}
          </p>
        )}

        {movie.overview && (
          <p className="text-[11px] text-white/40 leading-relaxed line-clamp-2">
            {movie.overview}
          </p>
        )}
      </div>
    </div>
  );
};

// ─── Assistant Message: text left + cards right ────────────────────────────────
const AssistantMessage = ({
  message,
  onMovieClick,
}: {
  message: ChatMessage;
  onMovieClick: (movie: Movie) => void;
}) => {
  const hasMovies = message.movies && message.movies.length > 0;

  return (
    <div className="flex gap-4 items-start w-full">
      {/* Left: AI text */}
      <div
        className={`glass-dark rounded-2xl p-5 ${
          hasMovies ? "flex-1 min-w-0" : "w-full"
        }`}
      >
        <ReactMarkdown className="prose dark:prose-invert max-w-none text-sm leading-relaxed">
          {message.content}
        </ReactMarkdown>

        {message.tools_used && message.tools_used.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {message.tools_used.map((tool) => (
              <span
                key={tool}
                className="text-xs px-2.5 py-1 bg-white/5 border border-white/10 rounded-full text-white/40"
              >
                {tool.replace("_", " ")}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Right: Movie cards panel */}
      {hasMovies && (
        <div
          className="shrink-0 rounded-2xl border border-white/10 bg-white/[0.03] overflow-y-auto"
          style={{ width: 260, maxHeight: 480 }}
        >
          <div className="px-3 pt-3 pb-1 border-b border-white/5">
            <p className="text-xs font-medium text-white/40 uppercase tracking-widest">
              {message.movies!.length === 1
                ? "1 Movie"
                : `${message.movies!.length} Movies`}
            </p>
          </div>
          <div className="p-2 space-y-1">
            {message.movies!.map((movie) => (
              <MovieCard key={movie.id} movie={movie} onClick={onMovieClick} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// ─── Main Chat Component ───────────────────────────────────────────────────────
const Chat: React.FC<ChatProps> = ({
  conversationId: initialConversationId,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(initialConversationId);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (conversationId) loadChatHistory();
  }, [conversationId]);

  const loadChatHistory = async () => {
    if (!conversationId) return;
    try {
      const history = await chatAPI.getHistory(conversationId);

      const loadedMessages: ChatMessage[] = history.messages.map(
        (msg: any, index: number) => {
          // For assistant messages, try to restore movies from localStorage cache
          const movies =
            msg.role === "assistant"
              ? getMoviesFromCache(conversationId, msg.content)
              : [];

          return {
            id: `${msg.role}-${index}`,
            role: msg.role,
            content: msg.content,
            timestamp: new Date(),
            movies,
            tools_used: msg.tools_used || [],
          };
        },
      );

      setMessages(loadedMessages);
    } catch (error) {
      console.error("Failed to load chat history:", error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(input, conversationId);

      const activeConvId = conversationId || response.conversation_id;

      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
        const saved = localStorage.getItem("conversations") || "[]";
        const conversations = JSON.parse(saved);
        if (!conversations.includes(response.conversation_id)) {
          conversations.push(response.conversation_id);
          localStorage.setItem("conversations", JSON.stringify(conversations));
        }
      }

      // ✅ Persist movies to localStorage so they survive history reload
      if (response.movies && response.movies.length > 0) {
        saveMoviesToCache(activeConvId, response.response, response.movies);
      }

      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: response.response,
        timestamp: new Date(),
        movies: response.movies || [],
        tools_used: response.tools_used || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (response.movies && response.movies.length > 0) {
        updateConversationTitle(activeConvId, response.movies[0].title);
      }
    } catch (error) {
      console.error("Failed to send message:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const updateConversationTitle = (convId: string, title: string) => {
    const saved = localStorage.getItem("conversationTitles") || "{}";
    const titles = JSON.parse(saved);
    if (!titles[convId]) {
      titles[convId] = title;
      localStorage.setItem("conversationTitles", JSON.stringify(titles));
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const newChat = () => {
    setMessages([]);
    setConversationId(undefined);
    setInput("");
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0a0a0f] via-[#14141e] to-[#1a1a2e]">
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onNewChat={newChat}
        onSelectConversation={(id) => setConversationId(id)}
      />

      <div className="flex-1 flex flex-col h-screen min-w-0">
        {/* ── Header ── */}
        <header className="border-b border-white/5 bg-black/30 backdrop-blur-xl px-6 py-4 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 hover:bg-white/5 rounded-xl transition-all duration-300 text-white/60 hover:text-white"
              aria-label="Toggle sidebar"
              type="button"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/20">
                <Film className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white tracking-tight shimmer-text">
                  MovieVerse AI
                </h1>
                <p className="text-xs text-white/40">Cinematic Intelligence</p>
              </div>
            </div>
          </div>
          <button
            onClick={newChat}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-xl transition-all duration-300 text-sm font-medium shadow-lg shadow-purple-500/25"
            type="button"
          >
            <Plus className="w-4 h-4" />
            New Chat
          </button>
        </header>

        {/* ── Messages ── */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-cinematic">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-8">
              <div className="relative">
                <div className="w-24 h-24 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-2xl flex items-center justify-center mb-6 animate-pulse">
                  <Film className="w-12 h-12 text-purple-400" />
                </div>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center animate-bounce">
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
              </div>
              <h2 className="text-3xl font-bold text-white mb-3 text-glow">
                Welcome to MovieVerse
              </h2>
              <p className="text-white/50 max-w-md text-lg font-light">
                Your intelligent cinematic companion. Discover, explore, and
                fall in love with movies.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-8 max-w-2xl w-full">
                {[
                  {
                    icon: <Film className="w-4 h-4" />,
                    text: "Find movies like Interstellar",
                  },
                  {
                    icon: <Clock className="w-4 h-4" />,
                    text: "Lord of the Rings watch order",
                  },
                  {
                    icon: <Star className="w-4 h-4" />,
                    text: "Movies by Christopher Nolan",
                  },
                  {
                    icon: <TrendingUp className="w-4 h-4" />,
                    text: "What should I watch tonight?",
                  },
                ].map((s) => (
                  <button
                    key={s.text}
                    onClick={() => {
                      setInput(s.text);
                      inputRef.current?.focus();
                    }}
                    className="glass-card p-4 text-left flex items-center gap-3 text-white/80 hover:text-white transition-all duration-300 group"
                    type="button"
                  >
                    <span className="text-purple-400 group-hover:text-purple-300 transition-colors">
                      {s.icon}
                    </span>
                    <span className="text-sm">{s.text}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {message.role === "user" ? (
                  <div className="max-w-xl rounded-2xl p-4 bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/20">
                    <ReactMarkdown className="prose dark:prose-invert max-w-none text-sm">
                      {message.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <div className="w-full">
                    <AssistantMessage
                      message={message}
                      onMovieClick={setSelectedMovie}
                    />
                  </div>
                )}
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex justify-start">
              <div className="glass-dark rounded-2xl p-5">
                <div className="flex items-center gap-3">
                  <div className="flex gap-1">
                    <span className="typing-dot w-2 h-2 bg-purple-400 rounded-full" />
                    <span className="typing-dot w-2 h-2 bg-purple-400 rounded-full" />
                    <span className="typing-dot w-2 h-2 bg-purple-400 rounded-full" />
                  </div>
                  <span className="text-sm text-white/40">
                    AI is thinking...
                  </span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* ── Input ── */}
        <div className="border-t border-white/5 bg-black/30 backdrop-blur-xl p-4 shrink-0">
          <form onSubmit={handleSubmit} className="max-w-5xl mx-auto">
            <div className="relative flex items-center gap-2">
              <div className="absolute left-4 top-1/2 -translate-y-1/2 text-white/20 pointer-events-none">
                <Film className="w-4 h-4" />
              </div>
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask me anything about movies..."
                rows={1}
                className="flex-1 resize-none rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm px-12 py-3.5 text-white placeholder:text-white/30 focus:outline-hidden focus:ring-2 focus:ring-purple-500/50 focus:border-transparent min-h-[52px] max-h-32 transition-all duration-300"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-2.5 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl transition-all duration-300 shadow-lg shadow-purple-500/25"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
            <p className="mt-2 text-center text-xs text-white/20">
              Powered by AI • Real-time movie data from TMDB
            </p>
          </form>
        </div>
      </div>

      {/* ── Movie Detail Modal ── */}
      {selectedMovie && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-xl z-50 flex items-center justify-center p-4 animate-in fade-in duration-300"
          onClick={() => setSelectedMovie(null)}
        >
          <div
            className="relative max-w-4xl w-full max-h-[90vh] overflow-y-auto rounded-2xl bg-[#1a1a2e] border border-white/10 p-6 scrollbar-cinematic"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setSelectedMovie(null)}
              className="absolute top-4 right-4 p-2 bg-white/5 hover:bg-white/10 rounded-xl transition-all duration-300 text-white/60 hover:text-white"
              type="button"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex flex-col md:flex-row gap-6">
              <div className="md:w-1/3 shrink-0">
                <div className="relative aspect-[2/3] rounded-xl overflow-hidden shadow-2xl">
                  {selectedMovie.poster_path ? (
                    <Image
                      src={`https://image.tmdb.org/t/p/w500${selectedMovie.poster_path}`}
                      alt={selectedMovie.title}
                      fill
                      className="object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center">
                      <Film className="w-16 h-16 text-white/20" />
                    </div>
                  )}
                </div>
              </div>

              <div className="flex-1 space-y-4">
                <div>
                  <h2 className="text-3xl font-bold text-white">
                    {selectedMovie.title}
                  </h2>
                  {selectedMovie.tagline && (
                    <p className="text-white/50 italic mt-1 text-sm">
                      "{selectedMovie.tagline}"
                    </p>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-3 text-sm text-white/60">
                  {selectedMovie.release_date && (
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      {new Date(selectedMovie.release_date).getFullYear()}
                    </span>
                  )}
                  {selectedMovie.runtime && (
                    <span className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {Math.floor(selectedMovie.runtime / 60)}h{" "}
                      {selectedMovie.runtime % 60}m
                    </span>
                  )}
                  {selectedMovie.vote_average && (
                    <span className="flex items-center gap-1 text-yellow-400 font-medium">
                      <Star className="w-4 h-4 fill-yellow-400" />
                      {selectedMovie.vote_average.toFixed(1)}
                    </span>
                  )}
                </div>

                {selectedMovie.vote_average && (
                  <StarRating rating={selectedMovie.vote_average} />
                )}

                {selectedMovie.genres && selectedMovie.genres.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {selectedMovie.genres.map((genre) => (
                      <span
                        key={genre}
                        className="px-3 py-1 bg-purple-500/15 border border-purple-500/20 rounded-full text-xs text-purple-300"
                      >
                        {genre}
                      </span>
                    ))}
                  </div>
                )}

                {selectedMovie.overview && (
                  <p className="text-white/70 leading-relaxed text-sm">
                    {selectedMovie.overview}
                  </p>
                )}

                {selectedMovie.director && (
                  <div className="flex items-center gap-2 text-sm">
                    <Clapperboard className="w-4 h-4 text-white/40" />
                    <span className="text-white/40">Director</span>
                    <span className="text-white/80 font-medium">
                      {selectedMovie.director}
                    </span>
                  </div>
                )}

                {selectedMovie.cast && selectedMovie.cast.length > 0 && (
                  <div>
                    <h4 className="text-xs font-medium text-white/40 uppercase tracking-widest mb-2">
                      Cast
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedMovie.cast.slice(0, 6).map((actor, index) => (
                        <span
                          key={index}
                          className="text-xs text-white/60 bg-white/5 border border-white/10 px-3 py-1 rounded-full"
                        >
                          {actor.name}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chat;
