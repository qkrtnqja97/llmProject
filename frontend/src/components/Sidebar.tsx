// // src/shared/components/Sidebar.tsx
// import React from "react";
// import { useLayout } from "../app/providers/LayoutProviders.tsx";

// // 메뉴 아이템 타입
// export interface SidebarMenuItem {
//   id: string;
//   label: string;
//   path?: string;
//   visible?: boolean;
// }

// // Sidebar가 받을 props 타입
// export interface SidebarProps {
//   loggedIn: boolean;
//   onLoginClick: () => void;
//   onOpenSettings?: () => void;
// }

// export const Sidebar: React.FC<SidebarProps> = ({
//   loggedIn,
//   onLoginClick,
//   onOpenSettings,
// }) => {
//   // menu만 쓰니까 나머지는 안 꺼내서 경고 제거
//   const { menu } = useLayout();

//   // m, item 타입 명시해서 implicit any 에러 제거
//   const visibleMenu = (menu as SidebarMenuItem[]).filter(
//     (m: SidebarMenuItem) => m.visible !== false
//   );

//   return (
//     <aside className="h-screen border-r bg-white flex flex-col">
//       <div className="flex items-center justify-between px-4 py-3 border-b">
//         <span className="font-semibold text-sm">Biz AI</span>

//         <div className="flex items-center gap-2">
//           {onOpenSettings && (
//             <button
//               className="text-xs px-2 py-1 rounded border border-zinc-200 text-zinc-600 hover:bg-zinc-50"
//               onClick={onOpenSettings}
//             >
//               설정
//             </button>
//           )}

//           {!loggedIn && (
//             <button
//               className="text-xs px-2 py-1 rounded bg-zinc-900 text-white"
//               onClick={onLoginClick}
//             >
//               로그인
//             </button>
//           )}
//         </div>
//       </div>

//       {/* 메뉴 렌더링 */}
//       <nav className="flex-1 px-2 py-3 space-y-1 text-sm">
//         {visibleMenu.map((item: SidebarMenuItem) => (
//           <button
//             key={item.id}
//             className="w-full text-left px-3 py-2 rounded-lg hover:bg-zinc-100"
//             onClick={() => console.log("navigate to", item.path)}
//           >
//             {item.label}
//           </button>
//         ))}
//       </nav>
//     </aside>
//   );
// };

// src/components/Sidebar.tsx
import React from "react";
import {
  MessageCircle,
  LayoutDashboard,
  FileText,
  Box,
  ShoppingCart,
  Package,
  Users,
  FolderClosed,
  History,
  User,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

// --- 타입들 ---

// 사이드바가 받는 props
export type SidebarProps = {
  // 접힘 여부 + 토글 버튼
  isCollapsed: boolean;
  onToggle: () => void;

  // 로그인 / 설정 영역 (옵션)
  loggedIn?: boolean;
  onLoginClick?: () => void;
  onOpenSettings?: () => void;
};

// 메뉴 아이템 그룹
type MenuGroup = "main" | "resource" | "relation" | "data" | "log";

// 메뉴 아이템 타입
type MenuItem = {
  label: string;
  icon: React.ReactNode;
  group: MenuGroup;
};

// --- 메뉴 데이터 ---

const menuItems: MenuItem[] = [
  { label: "AI 업무 검색", icon: <MessageCircle className="w-5 h-5" />, group: "main" },
  { label: "대시보드", icon: <LayoutDashboard className="w-5 h-5" />, group: "main" },

  { label: "업무 작성", icon: <FileText className="w-5 h-5" />, group: "resource" },

  { label: "재고 관리", icon: <Box className="w-5 h-5" />, group: "resource" },
  { label: "발주 관리", icon: <ShoppingCart className="w-5 h-5" />, group: "resource" },
  { label: "제품 관리", icon: <Package className="w-5 h-5" />, group: "resource" },

  { label: "연락처", icon: <Users className="w-5 h-5" />, group: "relation" },

  { label: "자료실", icon: <FolderClosed className="w-5 h-5" />, group: "data" },

  { label: "검색 기록", icon: <History className="w-5 h-5" />, group: "log" },
];

// --- 메인 Sidebar 컴포넌트 ---

export const Sidebar: React.FC<SidebarProps> = ({
  isCollapsed,
  onToggle,
  loggedIn = true,
  onLoginClick,
  onOpenSettings,
}) => {
  const widthClass = isCollapsed ? "w-[72px]" : "w-[260px]";

  const renderLabel = (text: string) =>
    isCollapsed ? null : <span className="text-sm">{text}</span>;

  return (
    <aside
      className={`h-screen border-r bg-white flex flex-col justify-between transition-all duration-200 ${widthClass}`}
    >
      {/* Top 영역 */}
      <div className="flex flex-col">
        {/* 로고 + 토글 버튼 */}
        <div className="flex items-center justify-between px-3 py-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-black flex items-center justify-center text-white text-xs font-semibold">
              B
            </div>
            {!isCollapsed && (
              <div className="flex flex-col leading-tight">
                <span className="text-sm font-semibold">Biz AI</span>
                <span className="text-[11px] text-zinc-500">
                  LLM/RAG Assistant
                </span>
              </div>
            )}
          </div>

          <button
            onClick={onToggle}
            className="p-1.5 rounded-full hover:bg-zinc-100 text-zinc-500"
          >
            {isCollapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* (옵션) 로그인 / 설정 버튼 영역 – 필요하면 여기 꾸며 쓰기 */}
        {!isCollapsed && (
          <div className="flex items-center justify-between px-3 pb-2 text-xs">
            <div className="text-zinc-500">
              {loggedIn ? "로그인 상태" : "로그아웃 상태"}
            </div>
            <div className="flex gap-2">
              {onOpenSettings && (
                <button
                  className="px-2 py-1 rounded border border-zinc-200 text-zinc-600 hover:bg-zinc-50"
                  onClick={onOpenSettings}
                >
                  설정
                </button>
              )}
              {!loggedIn && onLoginClick && (
                <button
                  className="px-2 py-1 rounded bg-zinc-900 text-white"
                  onClick={onLoginClick}
                >
                  로그인
                </button>
              )}
            </div>
          </div>
        )}

        {/* 메뉴 그룹들 */}
        <nav className="mt-2 space-y-4">
          <MenuGroup
            title={isCollapsed ? undefined : "AI & 개요"}
            items={menuItems.filter((m) => m.group === "main")}
            isCollapsed={isCollapsed}
          />
          <MenuGroup
            title={isCollapsed ? undefined : "업무 / 자원 관리"}
            items={menuItems.filter((m) => m.group === "resource")}
            isCollapsed={isCollapsed}
          />
          <MenuGroup
            title={isCollapsed ? undefined : "관계 관리"}
            items={menuItems.filter((m) => m.group === "relation")}
            isCollapsed={isCollapsed}
          />
          <MenuGroup
            title={isCollapsed ? undefined : "데이터 / 자료"}
            items={menuItems.filter((m) => m.group === "data")}
            isCollapsed={isCollapsed}
          />
          <MenuGroup
            title={isCollapsed ? undefined : "기록"}
            items={menuItems.filter((m) => m.group === "log")}
            isCollapsed={isCollapsed}
          />
        </nav>
      </div>

      {/* Bottom: 내 정보 / 설정 / 로그아웃 */}
      <div className="border-t px-3 py-3 space-y-2">
        <button
          className={`flex items-center gap-3 w-full px-2 py-2 rounded-xl hover:bg-zinc-100 text-xs text-zinc-700 ${
            isCollapsed ? "justify-center" : ""
          }`}
        >
          <User className="w-4 h-4" />
          {renderLabel("나의 정보")}
        </button>
        <button
          className={`flex items-center gap-3 w-full px-2 py-2 rounded-xl hover:bg-zinc-100 text-xs text-zinc-700 ${
            isCollapsed ? "justify-center" : ""
          }`}
          onClick={onOpenSettings}
        >
          <Settings className="w-4 h-4" />
          {renderLabel("설정")}
        </button>
        <button
          className={`flex items-center gap-3 w-full px-2 py-2 rounded-xl hover:bg-zinc-100 text-xs text-red-500 ${
            isCollapsed ? "justify-center" : ""
          }`}
        >
          <LogOut className="w-4 h-4" />
          {renderLabel("로그아웃")}
        </button>
      </div>
    </aside>
  );
};

// --- 메뉴 그룹 컴포넌트 ---

type MenuGroupProps = {
  title?: string;
  items: MenuItem[];
  isCollapsed: boolean;
};

const MenuGroup: React.FC<MenuGroupProps> = ({ title, items, isCollapsed }) => {
  if (!items.length) return null;

  return (
    <div className="px-2">
      {title && (
        <div className="text-[11px] text-zinc-400 font-medium px-2 mb-1">
          {title}
        </div>
      )}
      <div className="space-y-1">
        {items.map((item) => (
          <button
            key={item.label}
            className={`flex items-center gap-3 w-full px-2 py-2 rounded-xl hover:bg-zinc-100 text-sm text-zinc-700 ${
              isCollapsed ? "justify-center" : ""
            }`}
          >
            {item.icon}
            {!isCollapsed && <span>{item.label}</span>}
          </button>
        ))}
      </div>
    </div>
  );
};