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
  console.error("[startup] Falta VITE_GOOGLE_CLIENT_ID en las variables de entorno");
}

/* ────────────── Render raíz ─────────────────────── */
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <GoogleOAuthProvider clientId={googleClientId ?? ""}>
        <App />
      </GoogleOAuthProvider>
    </QueryClientProvider>
  </React.StrictMode>,
);
