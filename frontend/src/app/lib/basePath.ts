// Base path code here
import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://localhost:8000',
});