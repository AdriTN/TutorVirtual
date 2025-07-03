import {
  createContext, useContext, useEffect, useState, useCallback, useMemo, useRef,
} from 'react';
import {
  getAccessToken, setAccessToken, getRefreshToken, setRefreshToken,
  refreshAccessToken, clearTokens,
} from '@/services/auth';
import { jwtDecode } from 'jwt-decode';
import type { JwtPayload, AuthContextValue, UserData } from './auth.types'; // Import UserData
// Correctly import getUserMe from the new users endpoint file
import { logoutUser as apiLogoutUser } from '@/services/api/endpoints/auth';
import { getUserMe } from '@/services/api/endpoints/users';
import { useNotifications } from "@hooks/useNotifications";

const AuthContext = createContext<AuthContextValue | null>(null);

/* ------------------------------------------------------------------------ */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [accessToken, setAccessTokenState] = useState<string | null>(null);
  const [user, setUser]                    = useState<UserData | null>(null);
  const [isAdmin, setIsAdmin]              = useState(false);
  const [loading, setLoading]              = useState(true);
  const notifications = useNotifications();

  const notifySuccessRef = useRef(notifications.notifySuccess);
  const notifyInfoRef = useRef(notifications.notifyInfo);
  const notifyErrorRef = useRef(notifications.notifyError);

  useEffect(() => {
    notifySuccessRef.current = notifications.notifySuccess;
    notifyInfoRef.current = notifications.notifyInfo;
    notifyErrorRef.current = notifications.notifyError;
  }, [notifications.notifySuccess, notifications.notifyInfo, notifications.notifyError]);

  const fetchAndSetUser = useCallback(async (token: string) => {
    if (!token) {
      setUser(null);
      setIsAdmin(false);
      return;
    }
    try {
      const userData = await getUserMe(); // UserData should now include is_admin
      setUser(userData);
      setIsAdmin(userData.is_admin); // Use is_admin from API response
    } catch (error) {
      console.error("Failed to fetch user data:", error);
      notifyErrorRef.current("No se pudieron cargar los datos del usuario.");
      setUser(null);
      setIsAdmin(false);
    }
  }, []);

  const initializeAuth = useCallback(async () => {
    const storedAccess = getAccessToken();
    const storedRefresh = getRefreshToken();
    if (storedAccess && storedRefresh) {
      try {
        jwtDecode<JwtPayload>(storedAccess);
        setAccessTokenState(storedAccess);
        await fetchAndSetUser(storedAccess);
      } catch (e) {
        console.warn("Invalid stored access token on startup, clearing tokens.", e);
        clearTokens();
        setUser(null);
        setIsAdmin(false);
      }
    }
    setLoading(false);
  }, [fetchAndSetUser]);

  /* -------- carga inicial -------- */
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  /* -------- login / logout / refresh -------- */
  const login = useCallback(async (access: string, refresh: string) => {
    setAccessToken(access);
    setRefreshToken(refresh);
    setAccessTokenState(access);
    setLoading(true);
    await fetchAndSetUser(access);
    setLoading(false);
    notifySuccessRef.current("Sesión iniciada correctamente.");
  }, [fetchAndSetUser]);

  const logout = useCallback(async () => {
    const currentRefreshToken = getRefreshToken();
    if (currentRefreshToken) {
      try {
        await apiLogoutUser(currentRefreshToken);
      } catch (error) {
        console.error("Logout API call failed:", error);
      }
    }
    clearTokens();
    setAccessTokenState(null);
    setUser(null);
    setIsAdmin(false);
    notifyInfoRef.current("Has cerrado tu sesión.");
  }, []);

  const tryRefreshToken = useCallback(async () => {
    setLoading(true);
    try {
      const ok = await refreshAccessToken();
      if (!ok) {
        await logout();
        setLoading(false);
        return false;
      }
      const newAccess = getAccessToken();
      if (newAccess) {
        setAccessTokenState(newAccess);
        await fetchAndSetUser(newAccess);
      } else {
        await logout();
        setLoading(false);
        return false;
      }
      setLoading(false);
      return true;
    } catch (error) {
      console.error("Unexpected error during token refresh:", error);
      await logout();
      setLoading(false);
      return false;
    }
  }, [fetchAndSetUser, logout]);

  /* -------- memo value -------- */
  const value = useMemo<AuthContextValue>(() => ({
    isAuthenticated: Boolean(accessToken && user),
    isAdmin,
    accessToken,
    user,
    loading,
    login,
    logout,
    tryRefreshToken,
  }), [accessToken, user, isAdmin, loading, login, logout, tryRefreshToken]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/* hook público ----------------------------------------------------------- */
export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
};
