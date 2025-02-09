import axios from 'axios';

const axiosClient = axios.create({
  baseURL: 'https://127.0.0.1:8000/api',
  withCredentials: true, // Enable sending cookies with requests
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add response interceptor to handle 401 responses
axiosClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Redirect to login page on unauthorized access
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default axiosClient; 