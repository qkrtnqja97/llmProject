// src/routes/RequireAuth.tsx
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function RequireAuth() {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    // 로그인 안 돼 있으면 /login 으로 보내고
    // 돌아올 위치를 state에 기억해둠
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}