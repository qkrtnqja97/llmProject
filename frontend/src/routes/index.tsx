// src/routes/index.tsx
import { createBrowserRouter, Navigate } from "react-router-dom";
import MainLayout from "@layouts/MainLayout";
import HomePage from "@pages/Home/HomePage";
import AISearchPage from "@pages/AISearch/AISearchPage";
import Dashboard from "@pages/Dashboard/DashboardPage";
import ContactPage from "@pages/Contact/ContactPage";
import ResourcesPage from "@pages/Resource/ResourcePage";

import TaskCreatePage from "@pages/work/TaskCreate/TaskCreatePage";
import WorkLogPage from "@pages/work/WorkLog/WorkLogPage";
import MinutesPage from "@pages/work/Minute/MinutesPage";

import ProductManagePage from "@pages/manage/ProductManage/ProductManagePage";
import InventoryManagePage from "@pages/manage/InventoryManage/InventoryManagePage";
import OrderManagePage from "@pages/manage/OrderManage/OrderManagePage";

import EmployeeManagePage from "@pages/hr/EmployeeManage/EmployeeManagePage";
import AttendancePage from "@pages/hr/Attendance/AttendancePage";

import VoucherManagePage from "@pages/finance/VoucherManage/VoucherManagePage";
import SettlementPage from "@pages/finance/Settlement/SettlementPage";

import QuoteManagePage from "@pages/sales/QuoteManage/QuoteManagePage";
import OrderSo from "@pages/sales/OrderSo/OrderSoPage";

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
      { path: PATHS.HR.EMPLOYEES, element: <EmployeeManagePage /> },
      { path: PATHS.HR.ATTENDANCE, element: <AttendancePage /> },

      // --- 2. 회계/재무 그룹 ---
      {
        path: PATHS.FINANCE.VOUCHER,
        element: <VoucherManagePage />,
      },
      {
        path: PATHS.FINANCE.SETTLEMENT,
        element: <SettlementPage />,
      },

      // --- 3. 영업/판매 그룹 ---
      {
        path: PATHS.SALES.QUOTE,
        element: <QuoteManagePage />,
      },
      {
        path: PATHS.SALES.ORDER_SO,
        element: <OrderSo />,
      },

      // 업무관리 그룹
      { path: PATHS.WORK.CREATE, element: <TaskCreatePage /> },
      { path: PATHS.WORK.LOG, element: <WorkLogPage /> },
      { path: PATHS.WORK.MEMO, element: <MinutesPage /> },

      // 관리(물류) 그룹
      { path: PATHS.MANAGE.INVENTORY, element: <InventoryManagePage /> },
      {
        path: PATHS.MANAGE.ORDER,
        element: <OrderManagePage />,
      },
      { path: PATHS.MANAGE.PRODUCT, element: <ProductManagePage /> },

      // 기타 메뉴
      { path: PATHS.CONTACT, element: <ContactPage /> },
      { path: PATHS.RESOURCES, element: <ResourcesPage /> },
      { path: PATHS.HISTORY, element: <Placeholder title="검색기록" /> },
      { path: PATHS.SETTINGS, element: <Placeholder title="설정" /> },
    ],
  },
  {
    path: "*",
    element: <Navigate to={PATHS.HOME} replace />,
  },
]);
