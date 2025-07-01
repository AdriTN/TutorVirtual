import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import {
  getAccessToken,
  refreshAccessToken,
  clearTokens,
} from "@services/auth";
import { useNotifications } from "@hooks/useNotifications";

/* ------------------------------------------------------------------ */
/* 1) Instancia base ------------------------------------------------- */
/* ------------------------------------------------------------------ */
const apiUrl = import.meta.env.VITE_BACKEND_URL ?? "/api"

export const api = axios.create({
  baseURL: apiUrl,
  timeout: 10_000,
});

/* ------------------------------------------------------------------ */
/* 2) Request interceptor → añade Bearer token ---------------------- */
/* ------------------------------------------------------------------ */
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

/* ------------------------------------------------------------------ */
/* 3) Response interceptor → refresh token automático y manejo de errores */
/* ------------------------------------------------------------------ */
api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const { notifyError } = useNotifications();

    if (!error.response) {
      notifyError("Error de red o el servidor no responde.");
      return Promise.reject(error);
    }

    const { status, data } = error.response;
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (status === 401 && !original._retry) {
      original._retry = true;

      try {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
          original.headers.set('Authorization', `Bearer ${getAccessToken()}`);
          return api(original);
        }
      } catch (refreshError) {
        clearTokens();
        notifyError("Tu sesión ha expirado. Por favor, inicia sesión de nuevo.");
        window.location.replace("/login");
        return Promise.reject(error);
      }

      clearTokens();
      notifyError("Tu sesión ha expirado. Por favor, inicia sesión de nuevo.");
      window.location.replace("/login");
      return Promise.reject(error);
    }

    let errorMessage = "Ocurrió un error inesperado.";
    if (data && typeof data === 'object' && 'message' in data && typeof data.message === 'string') {
      errorMessage = data.message;
    } else if (typeof data === 'string' && data.length > 0) {
      errorMessage = data;
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    notifyError(errorMessage);

    return Promise.reject(error);
  },
);
