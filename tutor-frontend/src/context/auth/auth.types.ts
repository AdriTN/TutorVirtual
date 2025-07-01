/**
 * Decoded JWT payload que nos envía el backend.
 * Añade un índice `[key: string]` para no romperse
 * si el backend introduce nuevos campos.
 */
export interface JwtPayload {
  user_id:   number;
  is_admin:  boolean;
  exp:       number;
  [key: string]: unknown; 
}

/**
 * Forma completa del objeto que expone `useAuth()`.
 * Mantén los mismos nombres que el contexto para un
 * tipado automático y evitar duplicidades.
 */
export interface AuthContextValue {
  /* ---- estado ---- */
  isAuthenticated: boolean;
  isAdmin:         boolean;
  accessToken:     string | null;
  user:            UserData | null;
  loading:         boolean;

  /* ---- acciones ---- */
  login : (access: string, refresh: string) => void;
  logout: () => void;
  tryRefreshToken: () => Promise<boolean>;
}

export interface UserData {
  id: number;
  username: string;
  email: string;
}