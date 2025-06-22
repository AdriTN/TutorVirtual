import {
  createContext, useContext, useEffect, useState, useCallback, useMemo,
} from 'react';
import {
  getAccessToken, setAccessToken, getRefreshToken, setRefreshToken,
  refreshAccessToken, clearTokens,
} from '@/services/auth';
import { jwtDecode } from 'jwt-decode';
import type { JwtPayload, AuthContextValue } from './auth.types';

const AuthContext = createContext<AuthContextValue | null>(null);

/* ---------- utils ------------------------------------------------------- */
const isAdminFrom = (token: string): boolean => {
  try {
    return Boolean(jwtDecode<JwtPayload>(token).is_admin);
  } catch {
    return false;
  }
};

/* ------------------------------------------------------------------------ */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [accessToken, setAccessTokenState] = useState<string | null>(null);
  const [isAdmin, setIsAdmin]             = useState(false);
  const [loading, setLoading]             = useState(true);

  /* -------- carga inicial -------- */
  useEffect(() => {
    const storedAccess  = getAccessToken();
    const storedRefresh = getRefreshToken();
    if (storedAccess && storedRefresh) {
      setAccessTokenState(storedAccess);
      setIsAdmin(isAdminFrom(storedAccess));
    }
    setLoading(false);
  }, []);

  /* -------- login / logout / refresh -------- */
  const login = useCallback((access: string, refresh: string) => {
    setAccessToken(access);
    setRefreshToken(refresh);
    setAccessTokenState(access);
    setIsAdmin(isAdminFrom(access));
  }, []);

  const logout = useCallback(() => {
    clearTokens();
    setAccessTokenState(null);
    setIsAdmin(false);
  }, []);

  const tryRefreshToken = useCallback(async () => {
    const ok = await refreshAccessToken();
    if (!ok) {
      logout();
      return false;
    }
    const newAccess = getAccessToken();
    if (newAccess) {
      setAccessTokenState(newAccess);
      setIsAdmin(isAdminFrom(newAccess));
    }
    return true;
  }, [logout]);

  /* -------- memo value -------- */
  const value = useMemo<AuthContextValue>(() => ({
    isAuthenticated: Boolean(accessToken),
    isAdmin,
    accessToken,
    loading,
    login,
    logout,
    tryRefreshToken,
  }), [accessToken, isAdmin, loading, login, logout, tryRefreshToken]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/* hook público ----------------------------------------------------------- */
export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
};
