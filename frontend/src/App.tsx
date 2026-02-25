import React from "react";
import AppRoutes from "./routes";
import LoginOverlay from "./pages/LoginOverlay";
import { useAuth } from "./context/AuthContext";

const App: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <>
      <AppRoutes />
      {/* 로그인하지 않은 상태일 때만 오버레이 노출 */}
      {!isAuthenticated && <LoginOverlay />}
    </>
  );
};

export default App;
