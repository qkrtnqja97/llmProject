import React, { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import AppRoutes from "./routes";
import LoginOverlay from "./pages/LoginOverlay/LoginOverlay";
import { useAuth } from "./context/AuthContext";
import { useSettings } from "./context/SettingContext";
import { CompanyProvider } from "./context/CompanyContext";

const App: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { settings, isLoading } = useSettings();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (isLoading) return;

    if (isAuthenticated && location.pathname === "/" && settings?.startPage) {
      if (settings.startPage !== "/") {
        navigate(settings.startPage, { replace: true });
      }
    }
  }, [isAuthenticated, settings, location.pathname, navigate]);

  if (isLoading) {
    return <div className="loading-screen">설정을 불러오는 중...</div>;
  }

  return (
    /* ✅ CompanyProvider로 전체를 감싸서 Sidebar와 CompanyPage가 데이터를 공유하게 함 */
    <CompanyProvider>
      <AppRoutes />
      {!isAuthenticated && <LoginOverlay />}
    </CompanyProvider>
  );
};

export default App;
