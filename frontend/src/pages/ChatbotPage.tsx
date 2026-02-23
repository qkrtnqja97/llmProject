import React from "react";
import ChatbotPanel from "../components/ChatbotPanel";

const ChatbotPage: React.FC = () => {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">AI 어시스턴트</h2>
      <p className="text-xs text-zinc-500 mb-2">
        좌측 자료실·대시보드에서 문서를 추가한 뒤, 이 화면에서 질문을
        던져보세요.
      </p>
      <ChatbotPanel />
    </div>
  );
};

export default ChatbotPage;