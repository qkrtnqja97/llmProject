import React from "react";
import ChatPanel from "../components/chats/ChatPanel";

const ChatbotPage: React.FC = () => {
  return (
    <div className="space-y-4">
      <div className="pb-2">
        <h2 className="text-xl font-bold text-zinc-900">AI 어시스턴트</h2>
        <p className="text-sm text-zinc-500">
          사내 문서와 실시간 데이터를 기반으로 질문에 답변합니다.
        </p>
      </div>

      {/* 리팩토링된 통합 채팅 패널 */}
      <ChatPanel />
    </div>
  );
};

export default ChatbotPage;
