import axios from "axios";

const API_BASE_URL = "http://192.168.0.100:8000/v1/dashboard";

// 개별 거래 로그 타입
export interface TransactionLog {
  date: string;
  qty: number;
  type: "판매" | "구매";
}

// 월별 경영 실적 타입
export interface MonthlyStat {
  month: string;
  sales: number;
  purchase: number;
  profit: number;
}

// 요일별 판매 패턴 타입
export interface WeeklyPattern {
  weekday: string;
  dow: number;
  count: number;
}

// 성과 품목 공통 타입
export interface SalesItem {
  id: string; // part_number
  name: string; // part_number와 동일하게 쓰임
  category: string; // description
  amount: number; // 순이익
  sales: number; // 총 매출액
  purchase: number; // 총 매입액
  growth?: string;
  monthlyTrend?: Array<{
    month: string;
    sales: number;
    purchase: number;
    profit: number;
  }>;
}

// 대시보드 전체 데이터 구조
export interface DashboardSummary {
  topSales: Array<SalesItem>;
  botSales: Array<SalesItem>;
  topProductHistory: Array<TransactionLog>;
  monthlyStats: Array<MonthlyStat>;
  weeklyPattern: Array<WeeklyPattern>;
  lowInventory: {
    total_count: number;
    items: Array<{
      id: string;
      name: string;
      category: string;
      stock: number;
    }>;
  };
  upcomingEvents: Array<{
    date: string;
    title: string;
    type: string;
  }>;
}

export const dashboardService = {
  getSummary: async (
    year: number = 2026, // 📍 첫 번째 인자로 year 추가 (기본값 2026)
    days: number = 7,
    topY: number = 5,
    threshold: number = 300,
  ): Promise<DashboardSummary> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/summary`, {
        params: {
          year, // 📍 백엔드에 보낼 쿼리 파라미터에 추가
          days,
          top_y: topY,
          threshold,
        },
      });
      return response.data;
    } catch (error) {
      console.error("Dashboard API Error:", error);
      throw error;
    }
  },
};
