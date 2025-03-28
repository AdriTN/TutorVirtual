import { createContext, useContext, useState, useEffect, use } from "react";
import api from "../services/apis/backend-api/api";

interface AuthContextProps {
  isAuthenticated: boolean;
  access_token: string | null;
  refreshToken: string | null;
  loading: boolean;
  login: (token: string, refreshTkn: string) => void;
  logout: () => void;
  tryRefreshToken: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [access_token, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const accessToken = localStorage.getItem("accessToken");
    const refreshToken = localStorage.getItem("refreshToken");

    if (accessToken) {
      setAccessToken(accessToken);
      setIsAuthenticated(true);
    }

    if (refreshToken) {
      setRefreshToken(refreshToken);
    }

    setLoading(false);
  }
  , []);

  const login = (token: string, refreshTkn: string) => {
    setAccessToken(token);
    setRefreshToken(refreshTkn);
    setIsAuthenticated(true);
    localStorage.setItem("accessToken", token);
    localStorage.setItem("refreshToken", refreshTkn);
  };

  const logout = () => {
    setAccessToken(null);
    setRefreshToken(null);
    setIsAuthenticated(false);
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
  };

  const tryRefreshToken = async (): Promise<boolean> => {
    if (!refreshToken) {
      return false;
    }

    try {
      const response = await api.post("/api/refresh", {
        refresh_token: refreshToken,
      });

      const { new_access_token, new_refresh_token } = response.data;

      console.log("new_access_token:", new_access_token);
      console.log("new_refresh_token:", new_refresh_token);
      
      login(new_access_token, new_refresh_token);
      return true;
    } catch (error) {
      console.error("Error al refrescar el token:", error);
      logout();
      return false;
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, access_token, refreshToken, loading, login, logout, tryRefreshToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}
