import { createContext, useContext, useEffect, useState } from "react";
import {
  getAccessToken,
  setAccessToken,
  getRefreshToken,
  setRefreshToken,
  refreshAccessToken,
  clearTokens,
} from "../services/authService";
import { jwtDecode } from "jwt-decode";

type JwtPayload = {
  user_id: number;
  is_admin: boolean;
  exp: number;
};

interface AuthContextProps {
  isAuthenticated: boolean;
  isAdmin: boolean;
  accessToken: string | null;
  loading: boolean;
  login:  (access: string, refresh: string) => void;
  logout: () => void;
  tryRefreshToken: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  /* ------------- estado interno ------------- */
  const [accessToken, setAccessTokenState] = useState<string | null>(null);
  const [isAdmin,     setIsAdmin]          = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  /* -------- helper para extraer admin -------- */
  const extractAdmin = (token: string): boolean => {
    try {
      const payload = jwtDecode<JwtPayload>(token);
      return Boolean(payload.is_admin);
    } catch (error) {
      console.error("Error decoding token:", error);
      return false;
    }
  };

  /* -------- carga inicial -------- */
  useEffect(() => {
    const storedAccess  = getAccessToken();
    const storedRefresh = getRefreshToken();

    if (storedAccess && storedRefresh) {
      setAccessTokenState(storedAccess);
      setIsAdmin(extractAdmin(storedAccess));
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  /* -------- login -------- */
  const login = (access: string, refresh: string) => {
    /* persistir */
    setAccessToken(access);
    setRefreshToken(refresh);

    /* estado UI */
    setAccessTokenState(access);
    setIsAdmin(extractAdmin(access));
    setIsAuthenticated(true);
  };

  /* -------- logout -------- */
  const logout = () => {
    clearTokens();
    setAccessTokenState(null);
    setIsAdmin(false);
    setIsAuthenticated(false);
  };

  /* -------- refresh -------- */
  const tryRefreshToken = async () => {
    const ok = await refreshAccessToken();
    if (ok) {
      const newAccess = getAccessToken();
      if (newAccess) {
        setAccessTokenState(newAccess);
        setIsAdmin(extractAdmin(newAccess));
        setIsAuthenticated(true);
      }
    } else {
      logout();
    }
    return ok;
  };

  /* -------- contexto -------- */
  const value: AuthContextProps = {
    isAuthenticated,
    isAdmin,
    accessToken,
    loading,
    login,
    logout,
    tryRefreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/* hook de conveniencia */
export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};
