import type { MenuItem } from "../types";

const STORAGE_KEY = "biz-ai-layout";

export const defaultMenu: MenuItem[] = [
  { id: "home", label: "홈", path: "/", pinned: true, visible: true },
  { id: "ai", label: "AI 어시스턴트", path: "/ai", visible: true },
  { id: "dashboard", label: "대시보드", path: "/dashboard", visible: true },
  { id: "library", label: "자료실", path: "/library", visible: true },
  { id: "insights", label: "인사이트", path: "/insights", visible: true },
  { id: "company", label: "회사 설정", path: "/company", visible: true },
];

export const layoutStorage = {
  loadMenu: (): MenuItem[] => {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : defaultMenu;
  },
  saveMenu: (menu: MenuItem[]) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(menu));
  },
};
