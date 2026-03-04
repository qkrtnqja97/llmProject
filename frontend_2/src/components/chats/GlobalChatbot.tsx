/* src/components/chats/GlobalChatbot.tsx */
import React, {
  Dispatch,
  SetStateAction,
  useState,
  useEffect,
  useRef,
} from "react";
import * as LucideIcons from "lucide-react";
import ChatPanel from "./ChatPanel";
import { useChat } from "@context/ChatContext";
import { useAuth } from "@context/AuthContext";
import styles from "./GlobalChatbot.module.css";

interface GlobalChatbotProps {
  isOpen: boolean;
  setIsOpen: Dispatch<SetStateAction<boolean>>;
  isSettingsOpen: boolean;
  theme: string;
}

const GlobalChatbot: React.FC<GlobalChatbotProps> = ({
  isOpen,
  setIsOpen,
  isSettingsOpen,
}) => {
  // ✅ sendMessage를 가져와서 사용합니다.
  const { lastQuestion, lastAnswer, sendMessage } = useChat();
  const { user, userSettings } = useAuth();

  const [miniInput, setMiniInput] = useState("");
  const [isMiniLoading, setIsMiniLoading] = useState(false);
  const [showPreview, setShowPreview] = useState(true);

  const [position, setPosition] = useState({
    x: window.innerWidth - 80,
    y: 80,
  });

  const [isDragging, setIsDragging] = useState(false);
  const dragStartOffset = useRef({ x: 0, y: 0 });

  useEffect(() => {
    if (isSettingsOpen && isOpen) setIsOpen(false);
  }, [isSettingsOpen, isOpen, setIsOpen]);

  useEffect(() => {
    const handleResize = () => {
      setPosition((prev) => ({
        x: Math.min(prev.x, window.innerWidth - 70),
        y: Math.min(prev.y, window.innerHeight - 70),
      }));
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (isOpen) return;
    dragStartOffset.current = {
      x: e.clientX - position.x,
      y: e.clientY - position.y,
    };
    setIsDragging(false);

    const handleMouseMove = (moveEvent: MouseEvent) => {
      setIsDragging(true);
      const bubbleWidth = showPreview ? 320 : 30;
      const minX = bubbleWidth;
      const maxX = window.innerWidth - 80;
      const minY = 30;
      const maxY = window.innerHeight - 80;

      let newX = moveEvent.clientX - dragStartOffset.current.x;
      let newY = moveEvent.clientY - dragStartOffset.current.y;

      setPosition({
        x: Math.max(minX, Math.min(newX, maxX)),
        y: Math.max(minY, Math.min(newY, maxY)),
      });
    };

    const handleMouseUp = () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
  };

  const handleIconClick = () => {
    if (!isDragging) setIsOpen(true);
  };

  // ✅ 미니 입력창 전송 로직 수정
  const handleMiniSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!miniInput.trim() || isMiniLoading) return;

    const userPrompt = miniInput;
    const userId = (userSettings as any)?.emp_id || user || "guest";

    setMiniInput("");
    setIsMiniLoading(true);
    setShowPreview(true);

    try {
      // ✅ Context의 sendMessage를 호출하여 실시간 타이핑 효과와 백엔드 통신을 동시에 수행
      await sendMessage(userPrompt, userId, () => {
        setIsMiniLoading(false);
      });
    } catch (error) {
      console.error("미니챗 전송 에러:", error);
      setIsMiniLoading(false);
    }
  };

  if (isSettingsOpen) return null;

  return (
    <>
      <aside
        className={`${styles.chatPanel} ${isOpen ? styles.panelOpen : ""}`}
      >
        <div className={styles.chatHeader}>
          <div className={styles.title}>
            <LucideIcons.Bot size={20} className={styles.headerIcon} />
            <span>AI 업무 지원</span>
          </div>
          <button
            className={styles.minimizeBtn}
            onClick={() => setIsOpen(false)}
          >
            <LucideIcons.ChevronsRight size={20} />
          </button>
        </div>
        <div className={styles.chatBodyContainer}>
          <ChatPanel />
        </div>
      </aside>

      {!isOpen && (
        <div
          className={styles.floatingWrapper}
          style={{
            left: `${position.x}px`,
            top: `${position.y}px`,
          }}
          onMouseDown={handleMouseDown}
        >
          {showPreview && (
            <div
              className={styles.previewBubble}
              onMouseDown={(e) => e.stopPropagation()}
            >
              <button
                className={styles.closeBubbleBtn}
                onClick={(e) => {
                  e.stopPropagation();
                  setShowPreview(false);
                }}
                type="button"
              >
                <LucideIcons.X size={12} />
              </button>
              <div className={styles.previewContent}>
                {lastQuestion ? (
                  <>
                    <div className={styles.questionRow}>
                      <span className={styles.qBadge}>Q</span>
                      <span className={styles.text}>{lastQuestion}</span>
                    </div>
                    <div className={styles.answerRow}>
                      <span className={styles.aBadge}>A</span>
                      <span className={styles.text}>
                        {isMiniLoading && !lastAnswer
                          ? "생각 중..."
                          : lastAnswer || "답변 대기 중"}
                      </span>
                    </div>
                  </>
                ) : (
                  <div className={styles.emptyText}>도움이 필요하신가요?</div>
                )}
              </div>

              <form className={styles.miniInputForm} onSubmit={handleMiniSend}>
                <input
                  type="text"
                  placeholder="질문 입력..."
                  value={miniInput}
                  onChange={(e) => setMiniInput(e.target.value)}
                  disabled={isMiniLoading}
                />
                <button
                  type="submit"
                  disabled={isMiniLoading || !miniInput.trim()}
                >
                  {isMiniLoading ? (
                    <LucideIcons.Loader2 size={14} className={styles.spin} />
                  ) : (
                    <LucideIcons.Send size={14} />
                  )}
                </button>
              </form>
              <div className={styles.bubbleTail} />
            </div>
          )}

          <button
            className={styles.floatingBtn}
            onClick={handleIconClick}
            onContextMenu={(e) => {
              e.preventDefault();
              setShowPreview(true);
            }}
          >
            <LucideIcons.MessageCircleMore size={30} color="#fff" />
            {!showPreview && (
              <div className={styles.reopenHint}>
                <LucideIcons.MessageSquare size={8} color="#fff" fill="#fff" />
              </div>
            )}
          </button>
        </div>
      )}
    </>
  );
};

export default GlobalChatbot;
