import { Navigate, Outlet } from "react-router-dom";
import { useAuth }          from "@context/auth/AuthContext";

const GuestRoute = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) return null;

  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <Outlet />;
};

export default GuestRoute;

