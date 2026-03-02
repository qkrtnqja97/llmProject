import apiClient from "./apiClient";

// --- 인터페이스 정의 ---

// 제품 관리 (products 테이블 기반)
export interface ProductItem {
  part_number: string;
  description?: string;
  std_unit_cost: number;
  std_selling_price: number;
  manufacturer?: string;
  current_quantity?: number;
}

// 재고 현황 (current_products 테이블 기반)
export interface InventoryItem {
  part_number: string;
  description?: string;
  current_quantity: number;
  last_updated: string;
}

export const inventoryService = {
  /**
   * [제품 관리] 제품 목록 조회 (페이지네이션 포함)
   * @param skip 시작 지점
   * @param limit 가져올 개수 (기본 30개)
   * @param search 검색어 (선택 사항)
   */
  getProducts: async (skip = 0, limit = 30, search = "") => {
    const response = await apiClient.get(`/inventory/products`, {
      params: { skip, limit, search },
    });
    // 백엔드 응답 형태 예시: { items: ProductItem[], total: number }
    return response.data;
  },

  /**
   * [재고 관리] 실시간 재고 현황 조회
   */
  getCurrentInventory: async (skip = 0, limit = 10, search = "") => {
    const response = await apiClient.get(`/inventory/current`, {
      params: { skip, limit, search },
    });

    // 백엔드가 [{}, {}] 배열을 바로 보내므로 이를 객체로 변환
    const data = response.data;

    if (Array.isArray(data)) {
      return {
        items: data, // 보내주신 JSON 데이터가 여기 담깁니다.
        total: data.length, // 전체 개수 (페이징용)
      };
    }

    return data;
  },

  /**
   * [제품 상세] 특정 제품의 상세 정보 조회
   */
  getProductDetail: async (partNumber: string) => {
    const response = await apiClient.get(`/inventory/products/${partNumber}`);
    return response.data;
  },

  /**
   * [재고 수정] 특정 품목의 재고 수량 수동 조정 (필요 시)
   */
  updateQuantity: async (partNumber: string, quantity: number) => {
    const response = await apiClient.patch(`/inventory/current/${partNumber}`, {
      current_quantity: quantity,
    });
    return response.data;
  },
};
