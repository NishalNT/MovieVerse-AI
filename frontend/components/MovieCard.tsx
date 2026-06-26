"use client";

import React, { useState } from "react";
import {
  Star,
  Calendar,
  Clock,
  Play,
  Plus,
  Info,
  ExternalLink,
} from "lucide-react";
import { Movie } from "@/types";
import Image from "next/image";

interface MovieCardProps {
  movie: Movie;
  size?: "small" | "medium" | "large" | "hero";
  onViewDetails?: (movieId: number) => void;
}

const MovieCard: React.FC<MovieCardProps> = ({
  movie,
  size = "medium",
  onViewDetails,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  console.log(movie.poster_path);
  
  // In MovieCard.tsx, add this fallback
  const posterUrl =
    movie.poster_path && !imageError
      ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
      : "https://image.tmdb.org/t/p/original/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg";
  
  const backdropUrl =
    movie.backdrop_path && !imageError
      ? `https://image.tmdb.org/t/p/original${movie.backdrop_path}`
      : posterUrl;

  const formatRuntime = (minutes?: number) => {
    if (!minutes) return "";
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const formatDate = (date?: string) => {
    if (!date) return "";
    return new Date(date).getFullYear();
  };

  const formatRating = (rating?: number) => {
    if (!rating) return "N/A";
    return rating.toFixed(1);
  };

  if (size === "small") {
    return (
      <div className="flex items-center gap-3 p-2 hover:bg-white/5 rounded-lg transition-all cursor-pointer group">
        <div className="w-12 h-16 relative rounded-md overflow-hidden flex-shrink-0">
          <Image
            src={posterUrl}
            alt={movie.title}
            fill
            className="object-cover"
            onError={() => setImageError(true)}
          />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm truncate text-white/90 group-hover:text-white transition-colors">
            {movie.title}
          </p>
          <div className="flex items-center gap-2 text-xs text-white/50">
            <span>{formatDate(movie.release_date)}</span>
            {movie.vote_average && (
              <span className="flex items-center gap-0.5">
                <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                {formatRating(movie.vote_average)}
              </span>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (size === "hero") {
    return (
      <div
        className="relative rounded-2xl overflow-hidden h-[400px] group cursor-pointer"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <Image
          src={backdropUrl}
          alt={movie.title}
          fill
          className="object-cover transition-transform duration-700 group-hover:scale-105"
          onError={() => setImageError(true)}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />

        <div className="absolute bottom-0 left-0 right-0 p-8">
          <div className="flex items-start gap-6">
            <div className="w-32 h-48 rounded-lg overflow-hidden shadow-2xl flex-shrink-0 hidden sm:block">
              <Image
                src={posterUrl}
                alt={movie.title}
                width={128}
                height={192}
                className="object-cover"
                onError={() => setImageError(true)}
              />
            </div>
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-white mb-2">
                {movie.title}
              </h2>
              {movie.tagline && (
                <p className="text-white/60 text-sm italic mb-3">
                  "{movie.tagline}"
                </p>
              )}
              <div className="flex flex-wrap items-center gap-3 text-sm text-white/70 mb-3">
                {movie.release_date && (
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {formatDate(movie.release_date)}
                  </span>
                )}
                {movie.runtime && (
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {formatRuntime(movie.runtime)}
                  </span>
                )}
                {movie.vote_average && (
                  <span className="flex items-center gap-1 text-yellow-400">
                    <Star className="w-4 h-4 fill-yellow-400" />
                    {formatRating(movie.vote_average)}
                  </span>
                )}
              </div>
              <p className="text-white/80 text-sm line-clamp-2 max-w-2xl">
                {movie.overview}
              </p>
              <div className="flex gap-2 mt-4">
                {movie.genres?.slice(0, 3).map((genre) => (
                  <span
                    key={genre}
                    className="px-3 py-1 bg-white/10 rounded-full text-xs text-white/80"
                  >
                    {genre}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Medium/Large size
  return (
    <div
      className="group relative rounded-xl overflow-hidden movie-card"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div
        className={`relative ${size === "large" ? "aspect-[16/9]" : "aspect-[2/3]"}`}
      >
        <Image
          src={size === "large" ? backdropUrl : posterUrl}
          alt={movie.title}
          fill
          className="object-cover transition-transform duration-700 group-hover:scale-110"
          onError={() => setImageError(true)}
        />

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-80" />

        {/* Rating badge */}
        {movie.vote_average && (
          <div className="absolute top-3 right-3 glass-dark px-3 py-1.5 rounded-full flex items-center gap-1.5">
            <Star className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />
            <span className="text-white text-sm font-semibold">
              {formatRating(movie.vote_average)}
            </span>
          </div>
        )}

        {/* Content */}
        <div className="absolute bottom-0 left-0 right-0 p-4 text-white">
          <h3 className="text-lg font-bold truncate group-hover:text-purple-300 transition-colors">
            {movie.title}
          </h3>

          <div className="flex items-center gap-3 text-sm text-white/70 mt-1">
            {movie.release_date && (
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {formatDate(movie.release_date)}
              </span>
            )}
            {movie.runtime && size === "large" && (
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatRuntime(movie.runtime)}
              </span>
            )}
          </div>

          {movie.overview && size === "large" && (
            <p className="text-sm text-white/60 mt-2 line-clamp-2">
              {movie.overview}
            </p>
          )}

          {/* Hover actions */}
          <div
            className={`flex gap-2 mt-3 transition-all duration-300 ${
              isHovered
                ? "opacity-100 translate-y-0"
                : "opacity-0 translate-y-2"
            }`}
          >
            <button
              onClick={() => onViewDetails?.(movie.id)}
              className="flex-1 px-4 py-2 bg-purple-500 hover:bg-purple-600 rounded-lg text-sm font-medium transition-all duration-300 flex items-center justify-center gap-2"
            >
              <Info className="w-4 h-4" />
              View Details
            </button>
            <button className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-all duration-300 backdrop-blur-sm">
              <Play className="w-4 h-4" />
            </button>
            <button className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-all duration-300 backdrop-blur-sm">
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Hover overlay with cast info */}
        {isHovered && movie.cast && movie.cast.length > 0 && (
          <div className="absolute top-0 right-0 p-3">
            <div className="glass-dark rounded-lg p-3 max-w-[200px]">
              <p className="text-xs text-white/60 mb-1">Cast</p>
              <div className="space-y-1">
                {movie.cast.slice(0, 3).map((actor, index) => (
                  <div key={index} className="text-xs text-white/80 truncate">
                    {actor.name} as {actor.character}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MovieCard;
