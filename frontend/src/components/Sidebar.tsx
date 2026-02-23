import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useCompany } from "../context/CompanyContext";

type SidebarProps = {
  loggedIn: boolean;
  onLoginClick: () => void;
};

const navItems = [
  { to: "/", label: "홈", key: "home" },
  { to: "/ai", label: "AI 어시스턴트", key: "ai" },
  { to: "/dashboard", label: "대시보드", key: "dashboard" },
  { to: "/company", label: "회사 소개", key: "company" },
  { to: "/library", label: "자료실", key: "library" },
  { to: "/insights", label: "인사이트", key: "insights" },
];

const Sidebar: React.FC<SidebarProps> = ({ loggedIn, onLoginClick }) => {
  const { company } = useCompany();
  const navigate = useNavigate();

  return (
    <aside className="w-64 bg-white border-r border-zinc-200 flex flex-col py-5 px-4">
      {/* 로고 영역 */}
      <button
        type="button"
        onClick={() => navigate("/")}
        className="flex items-center gap-3 px-2 mb-6"
      >
        {company.logoUrl ? (
          <img
            src={company.logoUrl}
            alt={company.name}
            className="w-9 h-9 rounded-full object-cover shadow-sm"
          />
        ) : (
          <div className="w-9 h-9 rounded-full bg-zinc-900 text-white flex items-center justify-center text-sm font-bold">
            {company.name.slice(0, 2).toUpperCase()}
          </div>
        )}
        <div className="flex flex-col items-start">
          <span className="font-semibold tracking-tight text-sm">
            {company.name || "biz ai"}
          </span>
          <span className="text-[10px] text-zinc-400">
            Operations AI Portal
          </span>
        </div>
      </button>

      {/* 메뉴 */}
      <nav className="space-y-1 text-sm flex-1">
        {navItems.map((item) => (
          <NavLink
            key={item.key}
            to={item.to}
            className={({ isActive }) =>
              [
                "block px-3 py-2 rounded-xl transition-colors",
                isActive
                  ? "bg-zinc-900 text-white"
                  : "text-zinc-600 hover:bg-zinc-100",
              ].join(" ")
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* 로그인 상태 표시 */}
      <div className="mt-6 border-t pt-4 text-[11px] flex items-center justify-between text-zinc-400">
        <span>{loggedIn ? "사내 계정으로 로그인됨" : "게스트 모드"}</span>
        {!loggedIn && (
          <button
            type="button"
            onClick={onLoginClick}
            className="text-xs px-3 py-1 rounded-lg bg-zinc-900 text-white"
          >
            로그인
          </button>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;