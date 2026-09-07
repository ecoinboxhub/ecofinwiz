import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Skeleton from "./Skeleton";

export function ProtectedRoute({ children, adminOnly = false }: { children: React.ReactNode; adminOnly?: boolean }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center min-h-screen"><div className="space-y-4 w-72"><Skeleton variant="card" /><Skeleton variant="card" /><Skeleton variant="card" /></div></div>;
  if (!user) return <Navigate to="/login" replace />;
  if (adminOnly && !user.is_admin) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
}
