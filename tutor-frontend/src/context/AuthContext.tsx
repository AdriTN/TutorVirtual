import { createContext, useContext, useEffect, useState } from "react";
import {
  getAccessToken,
  setAccessToken,
  getRefreshToken,
  setRefreshToken,
  refreshAccessToken,
} from "../services/authService";

interface AuthContextProps {
  isAuthenticated: boolean;
  access_token?: string;
  loading: boolean;
  login: (access: string, refresh: string) => void;
  logout: () => void;
  tryRefreshToken: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  /* carga inicial */
  useEffect(() => {
    setIsAuthenticated(Boolean(getAccessToken()));
    setLoading(false);
  }, []);

  const login = (access: string, refresh: string) => {
    setAccessToken(access);
    setRefreshToken(refresh);
    setIsAuthenticated(true);
  };

  const logout = () => {
    sessionStorage.clear();
    setIsAuthenticated(false);
  };

  const tryRefreshToken = async () => {
    const ok = await refreshAccessToken();
    if (!ok) logout();
    setIsAuthenticated(ok);
    return ok;
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, loading, login, logout, tryRefreshToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};
