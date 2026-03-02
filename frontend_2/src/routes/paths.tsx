// src/routes/paths.tsx
export const PATHS = {
  HOME: "/home",
  AI_SEARCH: "/ai-search",
  DASHBOARD: "/dashboard",

  // 1. 인사/행정 (HR & Admin)
  HR: {
    EMPLOYEES: "/hr/employees",
    ATTENDANCE: "/hr/attendance",
    PAYROLL: "/hr/payroll",
  },

  // 2. 회계/재무 (Finance)
  FINANCE: {
    VOUCHER: "/finance/voucher",
    TAX: "/finance/tax",
    SETTLEMENT: "/finance/settlement",
  },

  // 3. 영업/판매 (Sales & CRM)
  SALES: {
    QUOTE: "/sales/quote",
    ORDER_SO: "/sales/order-so",
    CUSTOMER: "/sales/customer",
  },

  // 4. 생산/공정 (Production) - 필요 시 활성화
  PRODUCTION: {
    PLAN: "/production/plan",
    BOM: "/production/bom",
    PROCESS: "/production/process",
  },

  // 업무관리 그룹
  WORK: {
    CREATE: "/work/create",
    LOG: "/work/log",
    MEMO: "/work/memo",
  },

  // 관리(물류/재고) 그룹
  MANAGE: {
    INVENTORY: "/manage/inventory",
    ORDER: "/manage/order",
    PRODUCT: "/manage/product",
  },

  CONTACT: "/contact",
  RESOURCES: "/resources",
  HISTORY: "/history",
  SETTINGS: "/settings",
};
