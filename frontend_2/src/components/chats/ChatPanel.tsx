/* src/components/chats/ChatPanel.tsx */
import React, { useState, useRef, useEffect } from "react";
import { useChat } from "@context/ChatContext";
import { User, Bot, Send, Square } from "lucide-react";
import styles from "./ChatPanel.module.css";

const ChatPanel: React.FC = () => {
  const { messages, addMessage, simulateStreaming, stopStreaming } = useChat();
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || isTyping) return;

    addMessage({
      role: "user",
      content: input,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    });

    const userPrompt = input;
    setInput("");
    setIsTyping(true);

    // 응답 완료 시 isTyping을 false로 바꾸는 콜백 전달
    simulateStreaming(userPrompt, () => setIsTyping(false));
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

          {/* 📍 테마 대응: 중지 버튼의 색상을 인라인 대신 클래스나 변수로 관리 권장 */}
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
