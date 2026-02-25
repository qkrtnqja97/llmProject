import React from "react";
import type { ChatMessage } from "../../shared/types";
// ✅ CSS Module 임포트
import styles from "./MessageBubble.module.css";

interface MessageBubbleProps {
  message: ChatMessage;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isAssistant = message.role === "assistant";

  return (
    <div
      className={`${styles.wrapper} ${isAssistant ? styles.assistantWrapper : styles.userWrapper}`}
    >
      <div
        className={`${styles.bubble} ${isAssistant ? styles.assistantBubble : styles.userBubble}`}
      >
        {/* 본문 */}
        <div className={styles.content}>{message.content}</div>

        {/* 시간 정보 */}
        <div className={styles.timestamp}>
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
