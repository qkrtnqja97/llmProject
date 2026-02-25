import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

// 레이아웃 및 페이지
import AppLayout from "../components/layout/AppLayout";
import HomePage from "../pages/HomePage";
import ChatbotPage from "../pages/ChatbotPage";
import DashboardPage from "../pages/DashboardPage";
import CompanyPage from "../pages/CompanyPage";
import LibraryPage from "../pages/LibraryPage";
import InsightPage from "../pages/InsightPage";

/**
 * 인증 보호 가드
 */
const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/" replace />;
};

const AppRoutes = () => {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        {/* 누구나 접근 가능한 홈 */}
        <Route path="/" element={<HomePage />} />

        {/* 보호된 경로들 */}
        <Route
          path="/ai"
          element={
            <PrivateRoute>
              <ChatbotPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <DashboardPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/company"
          element={
            <PrivateRoute>
              <CompanyPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/library"
          element={
            <PrivateRoute>
              <LibraryPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/insights"
          element={
            <PrivateRoute>
              <InsightPage />
            </PrivateRoute>
          }
        />

        {/* 없는 페이지 접근 시 홈으로 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
};

export default AppRoutes;
