import React, { useEffect, useRef } from "react";
import { useChat } from "../../context/ChatContext";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";
import styles from "./ChatPanel.module.css";

const ChatPanel: React.FC = () => {
  const { messages, isSending, sendMessage } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isSending]);

  return (
    <div className={styles.container}>
      {/* 1. 메시지 스크롤 구역 */}
      <div ref={scrollRef} className={styles.scrollArea}>
        <div className={styles.innerContent}>
          {messages.length === 0 ? (
            <div className={styles.empty}>
              <p>대화를 시작해 보세요.</p>
            </div>
          ) : (
            <div className={styles.messageList}>
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
            </div>
          )}
          {isSending && <div className={styles.typing}>AI 답변 중...</div>}
        </div>
      </div>

      {/* 2. 하단 입력창 구역 (항상 바닥 고정) */}
      <div className={styles.inputSection}>
        <div className={styles.inputBox}>
          <ChatInput onSend={sendMessage} disabled={isSending} />
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
