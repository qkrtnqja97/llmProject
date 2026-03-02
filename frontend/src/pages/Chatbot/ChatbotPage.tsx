import React from "react";
import ChatPanel from "../../components/chats/ChatPanel";
import styles from "./ChatbotPage.module.css";

const ChatbotPage: React.FC = () => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>AI 어시스턴트</h2>
        <p className={styles.subtitle}>
          사내 문서와 실시간 데이터를 기반으로 질문에 답변합니다.
        </p>
      </div>

      <div className={styles.chatWrapper}>
        <ChatPanel />
      </div>
    </div>
  );
};

export default ChatbotPage;
