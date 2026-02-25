import React from "react";
import { useLocation } from "react-router-dom";

const Header: React.FC = () => {
  const location = useLocation();

  const getPageTitle = (path: string) => {
    const titles: Record<string, string> = {
      "/": "홈",
      "/ai": "AI 어시스턴트",
      "/dashboard": "운영 대시보드",
      "/library": "문서 자료실",
      "/insights": "비즈니스 인사이트",
      "/company": "회사 설정",
    };
    return titles[path] || "Console";
  };

  return (
    <header className="h-16 border-b border-zinc-100 bg-white/80 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-10">
      <h2 className="text-sm font-semibold text-zinc-800">
        {getPageTitle(location.pathname)}
      </h2>

      {/* ✅ 우측 사용자 정보 영역을 완전히 비워두거나 알림 아이콘 등을 넣을 수 있습니다 */}
      <div className="flex items-center gap-4">{/* 비워둠 */}</div>
    </header>
  );
};

export default Header;
