import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import {
  getAccessToken,
  refreshAccessToken,
  clearTokens,
} from "@services/auth";

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
/* 3) Response interceptor → refresh token automático ---------------- */
/* ------------------------------------------------------------------ */
api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    if (!error.response) return Promise.reject(error);

    const { status } = error.response;
    const original   = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // 401 → intentamos refresh una sola vez
    if (status === 401 && !original._retry) {
      original._retry = true;

      const refreshed = await refreshAccessToken();
      if (refreshed) {
        original.headers.set('Authorization', `Bearer ${getAccessToken()}`);
        return api(original);
      }

      /* refresh falló → sesión expirada */
      clearTokens();
      window.location.replace("/login");
    }

    return Promise.reject(error);
  },
);
