import {
  createContext, useContext, useEffect, useState, useCallback, useMemo,
} from 'react';
import {
  getAccessToken, setAccessToken, getRefreshToken, setRefreshToken,
  refreshAccessToken, clearTokens,
} from '@/services/auth';
import { jwtDecode } from 'jwt-decode';
import type { JwtPayload, AuthContextValue } from './auth.types';
import { logoutUser as apiLogoutUser } from '@/services/api/endpoints/auth';
import { useNotifications } from "@hooks/useNotifications"; // Importar hook

const AuthContext = createContext<AuthContextValue | null>(null);

/* ---------- utils ------------------------------------------------------- */
const isAdminFrom = (token: string): boolean => {
  try {
    return Boolean(jwtDecode<JwtPayload>(token).is_admin);
  } catch {
    // Si el token es inválido/corrupto, jwtDecode lanzará un error.
    // Esto será manejado en PrivateRoute o donde se use el token.
    // Aquí, si no se puede decodificar, asumimos que no es admin.
      return false;
  }
};

/* ------------------------------------------------------------------------ */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [accessToken, setAccessTokenState] = useState<string | null>(null);
  const [isAdmin, setIsAdmin]             = useState(false);
  const [loading, setLoading]             = useState(true);
  const { notifySuccess, notifyInfo } = useNotifications();

  /* -------- carga inicial -------- */
  useEffect(() => {
    const storedAccess  = getAccessToken();
    const storedRefresh = getRefreshToken();
    if (storedAccess && storedRefresh) {
      try {
        setIsAdmin(isAdminFrom(storedAccess));
        setAccessTokenState(storedAccess);
      } catch (e) {
        console.warn("Invalid stored access token on startup, clearing tokens.", e)
        clearTokens();
      }
    }
    setLoading(false);
  }, []);

  /* -------- login / logout / refresh -------- */
  const login = useCallback((access: string, refresh: string) => {
    setAccessToken(access);
    setRefreshToken(refresh);
    setAccessTokenState(access);
    setIsAdmin(isAdminFrom(access));
    notifySuccess("Sesión iniciada correctamente.");
  }, [notifySuccess]);

  const logout = useCallback(async () => {
    const refreshToken = getRefreshToken(); 
    
    if (refreshToken) {
      await apiLogoutUser(refreshToken);
    }

    clearTokens(); 
    setAccessTokenState(null); 
    setIsAdmin(false); 
    notifyInfo("Has cerrado tu sesión.");
  }, [notifyInfo]);

  const tryRefreshToken = useCallback(async () => {
    try {
      const ok = await refreshAccessToken();
      if (!ok) {
        // Si refreshAccessToken devuelve false, es probable que el refresh token haya expirado o sea inválido.
        // El interceptor de API (si el error vino de una llamada API) o PrivateRoute (si es proactivo)
        // ya debería haber llamado a notifyError y gestionado el logout.
        // Llamar a logout aquí asegura que el estado local se limpie.
        await logout();
        return false;
      }
      const newAccess = getAccessToken();
      if (newAccess) {
        setAccessTokenState(newAccess);
        setIsAdmin(isAdminFrom(newAccess));
      }
      return true;
    } catch (error) {
        // Esto podría capturar errores si refreshAccessToken mismo lanza una excepción inesperada
        // (aunque está diseñado para devolver boolean).
        console.error("Unexpected error during token refresh:", error);
        await logout();
        return false;
    }
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
