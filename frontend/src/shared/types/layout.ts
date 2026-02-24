// src/shared/types/layout.ts
export type LayoutTheme = "light" | "dark" | "auto";

export interface MenuItem {
  id: string;            // 고유 ID
  label: string;         // 메뉴 이름 (ex. "재고 관리")
  path: string;          // 라우트 경로 (ex. "/inventory")
  icon?: string;         // 나중에 아이콘 쓸 때용 (ex. "inventory")
  pinned?: boolean;      // 고정 여부
  visible?: boolean;     // 숨김 처리용
}

export interface LayoutOptions {
  sidebarCollapsed: boolean;
  theme: LayoutTheme;
}

export interface LayoutState {
  menu: MenuItem[];
  options: LayoutOptions;
}