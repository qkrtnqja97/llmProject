// src/shared/lib/layoutStorage.ts
import type { LayoutState } from "../types/layout";

const STORAGE_KEY = "suyeon-layout";

export const defaultLayoutState: LayoutState = {
  menu: [
    { id: "home", label: "홈", path: "/", pinned: true, visible: true },
    { id: "inventory", label: "재고 관리", path: "/inventory", visible: true },
    { id: "order", label: "발주 요청", path: "/order", visible: true },
    { id: "report", label: "보고서", path: "/report", visible: true },
  ],
  options: {
    sidebarCollapsed: false,
    theme: "auto",
  },
};

export function loadLayoutState(): LayoutState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultLayoutState;
    const parsed = JSON.parse(raw) as LayoutState;
    // 기본값 보정용 (새 필드 추가됐을 때)
    return {
      ...defaultLayoutState,
      ...parsed,
      options: {
        ...defaultLayoutState.options,
        ...parsed.options,
      },
    };
  } catch {
    return defaultLayoutState;
  }
}

export function saveLayoutState(state: LayoutState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // 저장 실패해도 앱 터지면 안 되니까 무시
  }
}