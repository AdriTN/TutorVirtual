export interface JwtPayload {
  user_id:   number;
  is_admin:  boolean;
  exp:       number;
  [key: string]: unknown; 
}

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
  is_admin: boolean;
}