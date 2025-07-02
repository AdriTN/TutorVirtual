import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import {
  getAccessToken,
  refreshAccessToken,
  clearTokens,
} from "@services/auth";
import { showErrorNotification } from "@hooks/useNotifications";

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

    if (!error.response) {
      showErrorNotification("Error de red o el servidor no responde.");
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
        showErrorNotification("Tu sesión ha expirado. Por favor, inicia sesión de nuevo.");
        window.location.replace("/login");
        return Promise.reject(error);
      }

      clearTokens();
      showErrorNotification("Tu sesión ha expirado. Por favor, inicia sesión de nuevo.");
      window.location.replace("/login");
      return Promise.reject(error);
    }

    let errorMessage = "Ocurrió un error inesperado.";
    // Prioritize 'detail' from FastAPI, then 'message', then string data, then Axios error message
    if (data && typeof data === 'object') {
      if ('detail' in data && typeof data.detail === 'string' && data.detail.length > 0) {
        errorMessage = data.detail;
      } else if ('message' in data && typeof data.message === 'string' && data.message.length > 0) {
        errorMessage = data.message;
      }
    } else if (typeof data === 'string' && data.length > 0) {
      errorMessage = data;
    } else if (error.message) { // Fallback to Axios error message
      errorMessage = error.message;
    }
    
    showErrorNotification(errorMessage);

    return Promise.reject(error);
  },
);
