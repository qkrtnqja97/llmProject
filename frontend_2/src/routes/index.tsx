// src/routes/index.tsx
import { createBrowserRouter, Navigate } from "react-router-dom";
import MainLayout from "@layouts/MainLayout";
import HomePage from "@pages/HomePage";
import Dashboard from "@pages/DashboardPage";
import ContactPage from "@pages/ContactPage";
import TaskCreatePage from "@pages/TaskCreatePage";
import AISearchPage from "@pages/AISearchPage";
import ProductManagePage from "@pages/ProductManagePage";
import InventoryManagePage from "@pages/InventoryManagePage";
import { PATHS } from "./paths";

const Placeholder = ({ title }: { title: string }) => (
  <div style={{ padding: "20px" }}>
    <h2>{title} 페이지 준비 중입니다.</h2>
  </div>
);

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { index: true, element: <Navigate to={PATHS.HOME} replace /> },
      { path: PATHS.HOME, element: <HomePage /> },
      { path: PATHS.AI_SEARCH, element: <AISearchPage /> },
      { path: PATHS.DASHBOARD, element: <Dashboard /> },

      // --- 1. 인사/행정 그룹 ---
      { path: PATHS.HR.EMPLOYEES, element: <Placeholder title="사원 관리" /> },
      { path: PATHS.HR.ATTENDANCE, element: <Placeholder title="근태 기록" /> },
      { path: PATHS.HR.PAYROLL, element: <Placeholder title="급여/정산" /> },

      // --- 2. 회계/재무 그룹 ---
      {
        path: PATHS.FINANCE.VOUCHER,
        element: <Placeholder title="전표 관리" />,
      },
      {
        path: PATHS.FINANCE.TAX,
        element: <Placeholder title="세금계산서 발행" />,
      },
      {
        path: PATHS.FINANCE.SETTLEMENT,
        element: <Placeholder title="결산 보고서" />,
      },

      // --- 3. 영업/판매 그룹 ---
      {
        path: PATHS.SALES.QUOTE,
        element: <Placeholder title="부품 견적 관리" />,
      },
      {
        path: PATHS.SALES.ORDER_SO,
        element: <Placeholder title="수주(SO) 관리" />,
      },
      {
        path: PATHS.SALES.CUSTOMER,
        element: <Placeholder title="거래처/CRM" />,
      },

      // --- 4. 생산/공정 그룹 ---
      {
        path: PATHS.PRODUCTION.PLAN,
        element: <Placeholder title="생산 계획" />,
      },
      { path: PATHS.PRODUCTION.BOM, element: <Placeholder title="BOM 관리" /> },
      {
        path: PATHS.PRODUCTION.PROCESS,
        element: <Placeholder title="공정 관리" />,
      },

      // 업무관리 그룹
      { path: PATHS.WORK.CREATE, element: <TaskCreatePage /> },
      { path: PATHS.WORK.LOG, element: <Placeholder title="일지 작성" /> },
      { path: PATHS.WORK.MEMO, element: <Placeholder title="회의록" /> },

      // 관리(물류) 그룹
      { path: PATHS.MANAGE.INVENTORY, element: <InventoryManagePage /> },
      {
        path: PATHS.MANAGE.ORDER,
        element: <Placeholder title="발주(PO) 관리" />,
      },
      { path: PATHS.MANAGE.PRODUCT, element: <ProductManagePage /> },

      // 기타 메뉴
      { path: PATHS.CONTACT, element: <ContactPage /> },
      { path: PATHS.RESOURCES, element: <Placeholder title="자료실" /> },
      { path: PATHS.HISTORY, element: <Placeholder title="검색기록" /> },
      { path: PATHS.SETTINGS, element: <Placeholder title="설정" /> },
    ],
  },
  {
    path: "*",
    element: <Navigate to={PATHS.HOME} replace />,
  },
]);
