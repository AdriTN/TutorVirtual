import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useViewMode } from "../context/ViewModeContext";
import { JSX } from "react";

const AdminRoute: React.FC<{ children: JSX.Element }> = ({ children }) => {
  const { loading: authLoading }   = useAuth();
  const { ready, mode }            = useViewMode();
  const { isAdmin }                = useAuth();

  if (authLoading || !ready) return null;

  const actingAsAdmin = isAdmin && mode === "admin";
  return actingAsAdmin ? children : <Navigate to="/" replace />;
};

export default AdminRoute;