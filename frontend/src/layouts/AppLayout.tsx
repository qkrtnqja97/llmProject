// src/app/layouts/AppLayout.tsx  (주석은 참고용!)
import React, { useState } from "react";
import { useLocation } from "react-router-dom";

import { Sidebar } from "../components/Sidebar";
import { MainHeader } from "../components/MainHeader";

// 홈 화면: 대시보드 + 채팅 2컬럼 레이아웃
import { ChatAndDashboard } from "../components/ChatAndDashboard";

// 플로팅용: 미니 챗창
import { ChatWindow as ChatWindow } from "../components/chat/ChatWindowmini";

import { LayoutSettings } from "../components/LayoutSettings";

export const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const location = useLocation();
  const isHome = location.pathname === "/" || location.pathname === "/home";

  return (
    <div className="min-h-screen flex bg-[#f5f5f7]">
      {/* 사이드바 */}
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed((prev) => !prev)}
        loggedIn={true}
        onLoginClick={() => console.log("login click")}
        onOpenSettings={() => setSettingsOpen(true)}
      />

      {/* 오른쪽 영역: 헤더 + 메인 콘텐츠 */}
      <div className="flex-1 flex flex-col min-w-0">
        <MainHeader />

        <main className="flex-1 relative">
          {/* 홈(/, /home)에서는 대시보드+챗 메인 화면 */}
          {isHome ? <ChatAndDashboard /> : children}

          {/* 홈이 아닐 때만 플로팅 챗봇 */}
          {!isHome && (
            <>
              {/* 플로팅 챗봇 버튼 */}
              <button
                type="button"
                onClick={() => setChatOpen((prev) => !prev)}
                className="fixed bottom-6 right-6 z-40 flex items-center justify-center w-14 h-14 rounded-full shadow-xl bg-black text-white text-2xl hover:scale-105 transition-transform"
              >
                💬
              </button>

              {/* 플로팅 챗봇 창 */}
              {chatOpen && (
                <div className="fixed bottom-24 right-6 z-40 w-96 h-[460px]">
                  <ChatWindow variant="floating" />
                </div>
              )}
            </>
          )}
        </main>
      </div>

      {/* 레이아웃 설정 모달 */}
      {settingsOpen && (
        <LayoutSettings onClose={() => setSettingsOpen(false)} />
      )}
    </div>
  );
};