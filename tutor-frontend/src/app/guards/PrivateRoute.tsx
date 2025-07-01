import { Navigate, Outlet } from "react-router-dom";
import { useEffect, useState } from "react";
import { jwtDecode }          from "jwt-decode";
import { useAuth }            from "@context/auth/AuthContext";
import { useNotifications }   from "@hooks/useNotifications";

interface Payload { exp: number }

const PrivateRoute = () => {
  const { isAuthenticated, accessToken, tryRefreshToken, loading, logout } = useAuth();
  const [checking, setChecking] = useState(true);
  const { notifyError } = useNotifications();

  useEffect(() => {
    if (loading) return;

    const verify = async () => {
      if (!isAuthenticated || !accessToken) {
        setChecking(false);
        return;
      }

      try {
        const { exp } = jwtDecode<Payload>(accessToken);
        if (exp < Date.now() / 1000) {
          const refreshed = await tryRefreshToken();
          if (!refreshed) {
          }
        }
      } catch (e) {
        console.error("Token inválido o corrupto:", e);
        notifyError("Error de sesión: Token inválido. Serás redirigido al login.");
        logout();
      }
      setChecking(false);
    };
    verify();
  }, [loading, isAuthenticated, accessToken, tryRefreshToken, logout, notifyError]);

  if (loading || checking) return null;
  
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default PrivateRoute;
