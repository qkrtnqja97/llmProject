import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useSettings } from "../context/SettingContext";

// 레이아웃 및 페이지
import AppLayout from "../components/layout/AppLayout";
import HomePage from "../pages/Homepage/HomePage";
import ChatbotPage from "../pages/Chatbot/ChatbotPage";
import DashboardPage from "../pages/Dashboard/DashboardPage";
import CompanyPage from "../pages/Company/CompanyPage";
import LibraryPage from "../pages/Library/LibraryPage";
import InsightPage from "../pages/Insight/InsightPage";
import TaskPage from "../pages/Task/TaskPage";
import InventoryPage from "../pages/Inventory/InventoryPage";
import OrderPage from "../pages/Order/OrderPage";
import ProductPage from "../pages/Product/ProductPage";
import ContactPage from "../pages/Contact/ContactPage";
import HistoryPage from "../pages/History/HistoryPage";

/**
 * 인증 보호 가드
 */
const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();
  const { isLoading } = useSettings();

  if (isLoading) return null;

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

        <Route
          path="/tasks"
          element={
            <PrivateRoute>
              <TaskPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/inventory"
          element={
            <PrivateRoute>
              <InventoryPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/orders"
          element={
            <PrivateRoute>
              <OrderPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/products"
          element={
            <PrivateRoute>
              <ProductPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/contacts"
          element={
            <PrivateRoute>
              <ContactPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/history"
          element={
            <PrivateRoute>
              <HistoryPage />
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
