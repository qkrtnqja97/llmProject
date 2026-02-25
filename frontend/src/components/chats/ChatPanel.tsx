import React, { useEffect, useRef } from "react";
import { useChat } from "../../context/ChatContext";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";
// ✅ CSS Module 임포트
import styles from "./ChatPanel.module.css";

const ChatPanel: React.FC = () => {
  const { messages, isSending, sendMessage } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);

  // 메시지 추가 시 자동 스크롤
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isSending]);

  return (
    <div className={styles.container}>
      {/* 메시지 영역 */}
      <div ref={scrollRef} className={styles.scrollArea}>
        {messages.length === 0 ? (
          <div className={styles.emptyState}>
            <span className={styles.emptyIcon}>🤖</span>
            <p className={styles.emptyText}>
              무엇을 도와드릴까요? 문서나 재고에 대해 물어보세요.
            </p>
          </div>
        ) : (
          <div className={styles.messageList}>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
          </div>
        )}

        {isSending && (
          <div className={styles.typingIndicator}>
            <div className={styles.typingBubble}>AI가 생각 중입니다...</div>
          </div>
        )}
      </div>

      {/* 입력 영역 */}
      <div className={styles.inputSection}>
        <ChatInput onSend={sendMessage} disabled={isSending} />
      </div>
    </div>
  );
};

export default ChatPanel;
