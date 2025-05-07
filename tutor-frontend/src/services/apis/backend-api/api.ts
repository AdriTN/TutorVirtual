import axios from "axios";
import {
  getAccessToken,
  refreshAccessToken,
} from "../../authService";

const apiUrl = import.meta.env.VITE_BACKEND_URL;   // http://localhost:8000/api
export const api = axios.create({ baseURL: apiUrl });

/* -------- request interceptor -------- */
api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

/* -------- response interceptor -------- */
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (!error.response) {              /* red / CORS error */
      return Promise.reject(error);
    }

    const { status } = error.response;
    const original = error.config;

    if (status === 401 && !original._retry) {
      original._retry = true;
      const ok = await refreshAccessToken();

      if (ok) {
        original.headers.Authorization = `Bearer ${getAccessToken()}`;
        return api(original);
      }
      sessionStorage.clear();           /* logout forzado */
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
