/* src/components/chats/ChatPanel.tsx */
import React, { useState, useRef, useEffect } from "react";
import { useChat } from "@context/ChatContext";
import { useAuth } from "@context/AuthContext"; // ✅ Auth 추가
import { User, Bot, Send, Square } from "lucide-react";
import styles from "./ChatPanel.module.css"; // .module.css 인 경우 경로 확인 필요

const ChatPanel: React.FC = () => {
  // ✅ simulateStreaming -> sendMessage로 변경
  const { messages, sendMessage, stopStreaming } = useChat();
  const { user, userSettings } = useAuth(); // ✅ 유저 정보 가져오기
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // 새 메시지가 올 때마다 자동 스크롤
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;

    const userPrompt = input;
    const userId = (userSettings as any)?.emp_id || user || "guest"; // ✅ 백엔드용 ID 추출

    setInput("");
    setIsTyping(true);

    try {
      // ✅ 실제 API 연동 함수 호출 (Context에서 메시지 추가 로직을 포함하므로 여기서 addMessage 중복 호출 방지)
      await sendMessage(userPrompt, userId, () => {
        setIsTyping(false);
      });
    } catch (error) {
      console.error("전송 에러:", error);
      setIsTyping(false);
    }
  };

  // 중지 버튼 클릭 시 호출
  const handleStop = () => {
    stopStreaming();
    setIsTyping(false);
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.messageList} ref={scrollRef}>
        {messages.length === 0 && (
          <div className={styles.welcomeSection}>
            <Bot size={56} className={styles.welcomeIcon} />
            <p>
              Biz AI 어시스턴트입니다.
              <br />
              무엇을 도와드릴까요?
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`${styles.messageWrapper} ${styles[msg.role]}`}
          >
            <div className={styles.avatar}>
              {msg.role === "user" ? <User size={18} /> : <Bot size={18} />}
            </div>
            <div className={styles.contentWrapper}>
              <div className={styles.senderName}>
                {msg.role === "user" ? "나" : "AI 비서"}
              </div>
              <div className={styles.bubbleAndInfo}>
                <div className={styles.bubble}>
                  {msg.role === "assistant" && msg.content === "" ? (
                    <div className={styles.loadingBubble}>
                      <span className={styles.dot}></span>
                      <span className={styles.dot}></span>
                      <span className={styles.dot}></span>
                    </div>
                  ) : (
                    msg.content
                  )}
                </div>
                {msg.isStopped && (
                  <div className={styles.stopNotice}>
                    응답이 중단되었습니다.
                  </div>
                )}
                <span className={styles.timestamp}>{msg.timestamp}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className={styles.inputArea}>
        <div className={styles.inputContainer}>
          <textarea
            placeholder={
              isTyping
                ? "AI가 응답을 생성 중입니다..."
                : "업무에 대해 질문해보세요..."
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey && !isTyping) {
                e.preventDefault();
                handleSend();
              }
            }}
            rows={1}
            disabled={isTyping}
          />

          {isTyping ? (
            <button
              onClick={handleStop}
              className={styles.stopButton}
              style={{ backgroundColor: "var(--accent-hover, #ef4444)" }}
            >
              <Square size={18} fill="currentColor" />
            </button>
          ) : (
            <button onClick={handleSend} disabled={!input.trim()}>
              <Send size={18} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
