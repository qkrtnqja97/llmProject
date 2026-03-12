/* src/shared/components/MainLayout.tsx */
import React, { useState, useEffect, useRef } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "@components/sidebar/Sidebar";
import GlobalChatbot from "@components/chats/GlobalChatbot";
import { useAuth } from "@context/AuthContext";
import { useModal } from "@hooks/useModal";
import LoginModal from "@components/modals/LoginModal";
import SettingsModal from "@components/modals/SettingsModal";
import TranslationModal from "@components/modals/TranslationModal";
import styles from "./MainLayout.module.css";

const MainLayout: React.FC = () => {
  const { user, userSettings, updateLocalSettings } = useAuth();
  const location = useLocation();

  // 1. 상태 관리
  const settingsModal = useModal();
  const translationModal = useModal();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(true);

  const prevChatState = useRef(isChatOpen);
  const isAiSearchPage = location.pathname === "/ai-search";

  // 2. 테마 제어 로직 (신규 테마 sand 포함)
  // 초기값은 navy로 설정하여 gray/sand의 밝은 테마 깜빡임을 방지
  const currentTheme = userSettings?.theme || "navy";

  useEffect(() => {
    // 📍 DOM에 테마 속성 주입 (CSS 변수 활성화)
    document.documentElement.setAttribute("data-theme", currentTheme);
    localStorage.setItem("theme", currentTheme);
  }, [currentTheme]);

  const handleSetTheme = (newTheme: string) => {
    // 📍 AuthContext를 통해 테마 변경 -> 전역 상태 변경 -> 위 useEffect 실행
    updateLocalSettings({ ...userSettings, theme: newTheme });
  };

  // 3. 설정 모달 핸들러 (챗봇 가림 로직 포함)
  const handleOpenSettings = () => {
    prevChatState.current = isChatOpen;
    setIsChatOpen(false); // 설정창 열릴 때 챗봇 잠시 닫음 (UI 간섭 방지)
    settingsModal.open();
  };

  const handleCloseSettings = () => {
    settingsModal.close();
    // 설정창 열기 전 챗봇이 열려있었다면 다시 복구
    if (prevChatState.current) {
      setIsChatOpen(true);
    }
  };

  // 4. 번역 모달 핸들러
  const handleOpenTranslation = () => {
    prevChatState.current = isChatOpen;
    setIsChatOpen(false);
    translationModal.open();
  };

  const handleCloseTranslation = () => {
    translationModal.close();
    if (prevChatState.current) {
      setIsChatOpen(true);
    }
  };

  // 5. 클래스 네임 조합 (CSS Module 대응)
  const contentClassName = `
    ${styles.content} 
    ${isCollapsed ? styles.sidebarCollapsed : ""} 
    ${isChatOpen && !isAiSearchPage ? styles.chatOpen : ""}
  `.trim();

  return (
    <div className={styles.container}>
      {/* 좌측 사이드바 */}
      <Sidebar
        isCollapsed={isCollapsed}
        onToggle={() => setIsCollapsed(!isCollapsed)}
        onOpenSettings={handleOpenSettings}
        /* 📍 점검 및 수정 사항:
           기존 onOpenProfile={handleOpenTranslation}으로 잘못 연결된 부분을
           Sidebar 컴포넌트 인터페이스에 맞춰 onOpenTranslation으로 수정하고,
           onOpenProfile에는 실제 프로필 관련 로직(필요시)을 연결해야 합니다.
        */
        onOpenTranslation={handleOpenTranslation}
      />

      {/* 중앙 메인 콘텐츠 영역 */}
      <main className={contentClassName}>
        <Outlet />
      </main>

      {/* 우측 챗봇 (로그인 유저 + AI 검색 페이지 아닐 때만) */}
      {user && !isAiSearchPage && (
        <GlobalChatbot
          isOpen={isChatOpen}
          setIsOpen={setIsChatOpen}
          isSettingsOpen={settingsModal.isOpen}
          theme={currentTheme}
        />
      )}

      {/* 미인증 유저 로그인 강제 */}
      {!user && <LoginModal isOpen={true} onClose={() => {}} />}

      {/* 환경 설정 모달 */}
      <SettingsModal
        isOpen={settingsModal.isOpen}
        onClose={handleCloseSettings}
        theme={currentTheme}
        setTheme={handleSetTheme}
      />

      {/* 번역 모달 */}
      <TranslationModal
        isOpen={translationModal.isOpen}
        onClose={handleCloseTranslation}
      />
    </div>
  );
};

export default MainLayout;
