import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Add response interceptor to ensure poster paths are included
api.interceptors.response.use(
  (response) => {
    // If the response has movies, ensure poster_path is preserved
    if (response.data && response.data.movies) {
      response.data.movies = response.data.movies.map((movie: any) => ({
        ...movie,
        poster_path: movie.poster_path || null,
        backdrop_path: movie.backdrop_path || null,
      }));
    }
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const chatAPI = {
  sendMessage: async (message: string, conversationId?: string) => {
    const response = await api.post('/api/chat', {
      message,
      conversation_id: conversationId,
    });
    return response.data;
  },
  
  getHistory: async (conversationId: string) => {
    const response = await api.get(`/api/chat/history/${conversationId}`);
    return response.data;
  },
  
  clearHistory: async (conversationId: string) => {
    const response = await api.delete(`/api/chat/history/${conversationId}`);
    return response.data;
  },
};

export const movieAPI = {
  searchMovies: async (query: string, page: number = 1) => {
    const response = await api.get('/api/movie/search', {
      params: { query, page },
    });
    return response.data;
  },
  
  getMovieDetails: async (movieId: number) => {
    const response = await api.get(`/api/movie/details/${movieId}`);
    return response.data;
  },
  
  getRecommendations: async (movieId: number, limit: number = 5) => {
    const response = await api.get(`/api/movie/recommendations/${movieId}`, {
      params: { limit },
    });
    return response.data;
  },
  
  getCollectionDetails: async (collectionId: number) => {
    const response = await api.get(`/api/movie/collection/${collectionId}`);
    return response.data;
  },
  
  getActorMovies: async (actorName: string) => {
    const response = await api.get(`/api/movie/actor/${encodeURIComponent(actorName)}`);
    return response.data;
  },
  
  getWatchOrder: async (collectionName: string) => {
    const response = await api.get('/api/movie/watch-order', {
      params: { collection_name: collectionName },
    });
    return response.data;
  },
  
  getTrending: async (timeWindow: string = 'week') => {
    const response = await api.get('/api/movie/trending', {
      params: { time_window: timeWindow },
    });
    return response.data;
  },
  
  getGenres: async () => {
    const response = await api.get('/api/movie/genres');
    return response.data;
  },
};