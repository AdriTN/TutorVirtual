// src/app/main.tsx
import React                  from "react";
import { createRoot }         from "react-dom/client";
import { GoogleOAuthProvider } from "@react-oauth/google";
import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";

import App from "@app/App";
import "@styles/globals.css";

/* ────────────── React-Query singleton ────────────── */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,     // 5 min
      refetchOnWindowFocus: false,
    },
  },
});

/* ────────────── Google OAuth guard ──────────────── */
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
if (!googleClientId) {
  // Este error es crítico para el funcionamiento de Google Login.
  // Podríamos lanzar una excepción o mostrar un mensaje muy visible.
  // Por ahora, mantenemos el console.error, ya que una notificación Toast podría no ser
  // visible si el resto de la app no puede inicializar.
  console.error(
    "[CRITICAL STARTUP ERROR] Falta VITE_GOOGLE_CLIENT_ID en las variables de entorno. "+
    "El inicio de sesión con Google no funcionará."
  );
}

/* ────────────── Render raíz ─────────────────────── */
const rootElement = document.getElementById("root");
if (rootElement) {
  createRoot(rootElement).render(
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <GoogleOAuthProvider clientId={googleClientId ?? ""}>
          <App />
        </GoogleOAuthProvider>
      </QueryClientProvider>
    </React.StrictMode>,
  );
} else {
  console.error(
    "[CRITICAL STARTUP ERROR] No se encontró el elemento raíz con ID 'root'. La aplicación no puede iniciarse."
  );
}
