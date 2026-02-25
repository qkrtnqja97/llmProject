import React, { useState } from "react";
// ✅ CSS Module 임포트
import styles from "./ChatInput.module.css";

interface ChatInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled }) => {
  const [text, setText] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim() && !disabled) {
      onSend(text);
      setText("");
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={
          disabled ? "AI가 응답을 생성하고 있습니다..." : "질문을 입력하세요..."
        }
        className={styles.input}
        disabled={disabled}
      />
      <button
        type="submit"
        disabled={disabled || !text.trim()}
        className={styles.sendBtn}
      >
        <span className={styles.btnText}>전송</span>
        {/* 아이콘을 넣고 싶다면 여기에 추가 가능 */}
      </button>
    </form>
  );
};

export default ChatInput;
