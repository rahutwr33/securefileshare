import axios from 'axios';
import { sessionManager } from './session';
import { store } from '../store';
import { logout, sessionExpired } from '../store/slices/authSlice';

const axiosClient = axios.create({
  baseURL: 'https://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for auth token
axiosClient.interceptors.request.use(
  (config) => {
    const token = sessionManager.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for token refresh
axiosClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // Check if token is expired
      sessionManager.clearSession();
      store.dispatch(sessionExpired());
      location.href = '/login';
      return Promise.reject(new Error('Session expired'));

    
    }
    return Promise.reject(error);
  }
);

export default axiosClient; 