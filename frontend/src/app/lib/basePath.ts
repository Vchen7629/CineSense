// Base path code here
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

export const backend_api = axios.create({
  baseURL: API_BASE_URL,
});

export const tmdb_api = axios.create({
  baseURL: 'https://api.themoviedb.org/3/'
})

