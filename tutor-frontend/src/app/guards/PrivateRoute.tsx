import { Navigate, Outlet } from "react-router-dom";
import { useEffect, useState } from "react";
import { jwtDecode }          from "jwt-decode";
import { useAuth }            from "@context/auth/AuthContext";

interface Payload { exp: number }

const PrivateRoute = () => {
  const { isAuthenticated, accessToken, tryRefreshToken, loading } = useAuth();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    if (loading) return;

    const verify = async () => {
      if (!isAuthenticated || !accessToken) return setChecking(false);

      try {
        const { exp } = jwtDecode<Payload>(accessToken);
        if (exp < Date.now() / 1000) await tryRefreshToken();
      } catch (e) {
        console.error("Token inválido:", e);
      }
      setChecking(false);
    };
    verify();
  }, [loading, isAuthenticated, accessToken, tryRefreshToken]);

  if (loading || checking) return null;
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default PrivateRoute;
