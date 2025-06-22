import { Navigate, Outlet } from "react-router-dom";
import { useAuth }          from "@context/auth/AuthContext";
import { useViewMode }      from "@context/view-mode/ViewModeContext";

const AdminRoute = () => {
  const { isAdmin, loading } = useAuth();
  const { mode, ready }      = useViewMode();

  if (loading || !ready) return null;
  return isAdmin && mode === "admin" ? <Outlet /> : <Navigate to="/" replace />;
};

export default AdminRoute;
