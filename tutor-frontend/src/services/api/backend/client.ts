import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import {
  getAccessToken,
  refreshAccessToken,
  clearTokens,
} from "@services/auth";
import { showErrorNotification } from "@hooks/useNotifications";
import { log } from "node:console";

/* ------------------------------------------------------------------ */
/* 1) Instancia base ------------------------------------------------- */
/* ------------------------------------------------------------------ */
const apiUrl = import.meta.env.VITE_BACKEND_URL ?? "/api"

export const api = axios.create({
  baseURL: apiUrl,
  timeout: 30_000,
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
          const newAccessToken = getAccessToken();
          console.log('Token para reintento:', newAccessToken);
          if (newAccessToken) {
            original.headers.set('Authorization', `Bearer ${newAccessToken}`);
          } else {
            console.error('¡El nuevo token de acceso es nulo después del refresh!');
            // Considerar logout si no se puede obtener el nuevo token
            clearTokens();
            showErrorNotification("Error crítico al refrescar sesión. Inicia sesión.");
            window.location.replace("/login");
            return Promise.reject(error);
          }
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
    if (data && typeof data === 'object') {
      if ('detail' in data && typeof data.detail === 'string' && data.detail.length > 0) {
        errorMessage = data.detail;
      } else if ('message' in data && typeof data.message === 'string' && data.message.length > 0) {
        errorMessage = data.message;
      }
    } else if (typeof data === 'string' && data.length > 0) {
      errorMessage = data;
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    showErrorNotification(errorMessage);

    return Promise.reject(error);
  },
);
