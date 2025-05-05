import axios from "axios";
import { useAuth } from "../../../context/AuthContext";


const apiUrl = import.meta.env.VITE_BACKEND_URL;  // "http://localhost:8000"

export const api = axios.create({
  baseURL: apiUrl,
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("accessToken");
  if (token) {
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // Aqui necesitamos acceso a "tryRefreshToken" de AuthContext.tsx
      const { tryRefreshToken } = useAuth();

      const success = await tryRefreshToken();

      if (success) {
        originalRequest.headers["Authorization"] = `Bearer ${sessionStorage.getItem("accessToken")}`;
        return api.request(originalRequest);
      } else {
        window.location.href = "/home";
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
  