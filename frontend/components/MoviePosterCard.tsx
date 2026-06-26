'use client';

import React, { useState } from 'react';
import { Star, Calendar, Clock, Play, Plus, Info } from 'lucide-react';
import { Movie } from '@/types';
import Image from 'next/image';

interface MoviePosterCardProps {
  movie: Movie;
  size?: 'small' | 'medium' | 'large';
  onViewDetails?: (movieId: number) => void;
}

const MoviePosterCard: React.FC<MoviePosterCardProps> = ({ 
  movie, 
  size = 'medium', 
  onViewDetails 
}) => {
  const [imageError, setImageError] = useState(false);
  
  const posterUrl = movie.poster_path && !imageError
    ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : null;

  const formatDate = (date?: string) => {
    if (!date) return '';
    return new Date(date).getFullYear();
  };

  const formatRating = (rating?: number) => {
    if (!rating) return 'N/A';
    return rating.toFixed(1);
  };

  const sizeClasses = {
    small: 'w-32',
    medium: 'w-48',
    large: 'w-64'
  };

  const heightClasses = {
    small: 'h-48',
    medium: 'h-72',
    large: 'h-96'
  };

  return (
    <div 
      className={`${sizeClasses[size]} flex-shrink-0 group cursor-pointer transition-all duration-300 hover:scale-105`}
      onClick={() => onViewDetails?.(movie.id)}
    >
      <div className={`relative ${heightClasses[size]} rounded-xl overflow-hidden shadow-lg group-hover:shadow-2xl transition-shadow duration-300`}>
        {posterUrl ? (
          <>
            <Image
              src={posterUrl}
              alt={movie.title}
              fill
              className="object-cover"
              onError={() => setImageError(true)}
            />
            {/* Hover Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-4">
              <div className="w-full">
                <h4 className="text-white text-sm font-semibold truncate">
                  {movie.title}
                </h4>
                <div className="flex items-center gap-2 text-xs text-white/60 mt-1">
                  {movie.release_date && (
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {formatDate(movie.release_date)}
                    </span>
                  )}
                  {movie.vote_average && (
                    <span className="flex items-center gap-0.5">
                      <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                      {formatRating(movie.vote_average)}
                    </span>
                  )}
                </div>
                <button className="mt-2 w-full px-3 py-1.5 bg-purple-500 hover:bg-purple-600 rounded-lg text-xs text-white transition-colors flex items-center justify-center gap-1">
                  <Info className="w-3 h-3" />
                  View Details
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-purple-500/10 to-pink-500/10 flex flex-col items-center justify-center rounded-xl border border-white/5">
            <div className="text-white/20 text-4xl mb-2">🎬</div>
            <span className="text-white/30 text-xs text-center px-2 line-clamp-2">{movie.title}</span>
          </div>
        )}
        
        {/* Rating Badge */}
        {movie.vote_average && (
          <div className="absolute top-2 right-2 bg-black/60 backdrop-blur-sm px-2 py-1 rounded-lg flex items-center gap-1">
            <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
            <span className="text-white text-xs font-medium">{formatRating(movie.vote_average)}</span>
          </div>
        )}
      </div>
      
      {/* Title below poster */}
      <div className="mt-2">
        <h4 className="text-white/80 text-sm font-medium truncate group-hover:text-white transition-colors">
          {movie.title}
        </h4>
        <div className="flex items-center gap-2 text-xs text-white/40">
          {movie.release_date && (
            <span>{formatDate(movie.release_date)}</span>
          )}
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
};

export default MoviePosterCard;