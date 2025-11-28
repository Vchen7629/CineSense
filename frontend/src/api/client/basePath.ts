// Base path code here
import axios from 'axios';

const RECOMMENDATION_API_BASE_URL = import.meta.env.VITE_RECOMMENDATION_API_BASE_URL || 'http://localhost:8000';
const USER_AUTH_API_BASE_URL = import.meta.env.VITE_USER_AUTH_API_BASE_URL || 'http://localhost:8001';

export const user_auth_api = axios.create({
  baseURL: USER_AUTH_API_BASE_URL,
});

export const recommendations_api = axios.create({
  baseURL: RECOMMENDATION_API_BASE_URL,
});

export const tmdb_api = axios.create({
  baseURL: 'https://api.themoviedb.org/3/'
})

