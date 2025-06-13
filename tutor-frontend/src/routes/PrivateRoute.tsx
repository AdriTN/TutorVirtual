import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { JSX } from "react";
import { jwtDecode } from "jwt-decode";
import { useEffect, useState } from "react";

interface TokenPayload {
  exp: number;
  [key: string]: any;
}

interface PrivateRouteProps {
  children: JSX.Element;
}

const PrivateRoute = ({ children }: PrivateRouteProps) => {
  const { isAuthenticated, accessToken, tryRefreshToken, loading } = useAuth();
  const [verifying, setVerifying] = useState(true);

  useEffect(() => {
    if (loading) {
      return;
    }

    const verifyToken = async () => {
      if (!isAuthenticated || !accessToken) {
        setVerifying(false);
        return;
      }

      try {
        const decodedToken = jwtDecode<TokenPayload>(accessToken);
        const now = Date.now().valueOf() / 1000;

        if (decodedToken.exp < now) {
          const success = await tryRefreshToken();

          if (!success) {
            setVerifying(false);
            return;
          }
        }
      } catch (error) {
        console.error("Error al verificar token:", error);
      }

      setVerifying(false);
    };

    verifyToken();
  }
  , [isAuthenticated, accessToken, loading, tryRefreshToken]);

  if (loading || verifying) {
    return <div>Cargando...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return children;
};


export default PrivateRoute;
