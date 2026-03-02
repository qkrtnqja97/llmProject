import React, { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";
import Header from "./Header";
import ChatPanel from "../chats/ChatPanel";
import { useChat } from "../../context/ChatContext";
import styles from "./AppLayout.module.css";

const AppLayout: React.FC = () => {
  const location = useLocation();
  const { messages, sendMessage, isSending } = useChat();
  const isAiPage = location.pathname === "/ai";

  const [chatMode, setChatMode] = useState<"panel" | "minimized">("panel");
  const [miniInput, setMiniInput] = useState("");

  // 최신 질문/답변 추출
  const lastUserMsg =
    [...messages].reverse().find((m) => m.role === "user")?.content ||
    "질문을 입력하세요.";
  const lastAiMsg =
    [...messages].reverse().find((m) => m.role === "assistant")?.content ||
    "대기 중...";

  const handleMiniSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!miniInput.trim() || isSending) return;
    sendMessage(miniInput);
    setMiniInput("");
  };

  return (
    <div className={styles.appRoot}>
      <Sidebar />
      <div className={styles.mainContainer}>
        <div className={styles.centerContent}>
          <Header />
          <main
            className={`${styles.content} ${isAiPage ? styles.aiPageContent : ""}`}
          >
            <div
              className={
                isAiPage ? styles.aiPageMaxContainer : styles.maxContainer
              }
            >
              <Outlet />
            </div>
          </main>
        </div>

        {/* ✅ /ai 페이지가 아닐 때만 우측 사이드바/프리뷰 노출 */}
        {!isAiPage && (
          <aside
            className={`${styles.rightSection} ${chatMode === "minimized" ? styles.isMinimized : ""}`}
          >
            {chatMode === "panel" ? (
              /* --- [모드 1] 우측 사이드바 --- */
              <div className={styles.sidePanel}>
                <div className={styles.panelHeader}>
                  <span className={styles.panelTitle}>AI Assistant</span>
                  <button
                    className={styles.minimizeBtn}
                    onClick={() => setChatMode("minimized")}
                  >
                    <span className={styles.minimizeIcon}></span>
                  </button>
                </div>
                <div className={styles.panelBody}>
                  <ChatPanel />
                </div>
              </div>
            ) : (
              /* --- [모드 2] 하단 프리뷰 바 + 입력창 + 스티커 --- */
              <div className={styles.miniFloatingGroup}>
                <div
                  className={styles.previewBox}
                  onDoubleClick={() => setChatMode("panel")}
                >
                  <div className={styles.historyArea}>
                    <div className={styles.miniLine}>
                      <b className={styles.q}>Q.</b> <span>{lastUserMsg}</span>
                    </div>
                    <div className={styles.miniLine}>
                      <b className={styles.a}>A.</b> <span>{lastAiMsg}</span>
                    </div>
                  </div>
                  <form
                    onSubmit={handleMiniSend}
                    className={styles.miniInputForm}
                  >
                    <input
                      type="text"
                      value={miniInput}
                      onChange={(e) => setMiniInput(e.target.value)}
                      placeholder="바로 질문하기..."
                      disabled={isSending}
                    />
                    <button
                      type="submit"
                      disabled={isSending || !miniInput.trim()}
                    >
                      {isSending ? "..." : "↵"}
                    </button>
                  </form>
                </div>
                <div
                  className={styles.mainSticker}
                  onClick={() => setChatMode("panel")}
                >
                  🤖
                </div>
              </div>
            )}
          </aside>
        )}
      </div>
    </div>
  );
};

export default AppLayout;
