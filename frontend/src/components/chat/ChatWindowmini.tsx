// src/components/chat/ChatWindow.tsx
import React, { useState } from "react";
import { useChat } from "../../context/ChatContext";
import type { KeyboardEventHandler } from "react";


type ChatWindowProps = {
  variant?: "full" | "floating"; // 스타일만 조금 다르게 줄 수 있게
};

export const ChatWindow: React.FC<ChatWindowProps> = ({ variant = "full" }) => {
  const { messages, loading, sendMessage, resetChat } = useChat();
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;
    const text = input;
    setInput("");
    await sendMessage(text);
  };

  const handleKeyDown: KeyboardEventHandler<HTMLInputElement> = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSend();
    }
  };

  const isFull = variant === "full";

  return (
    <div
      className={
        "flex h-full flex-col bg-white border border-zinc-200 " +
        (isFull
          ? "rounded-3xl shadow-sm"
          : "rounded-2xl shadow-2xl")
      }
    >
      {/* 헤더 */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-200 bg-zinc-50">
        <div className="flex flex-col">
          <span className="text-sm font-semibold">Biz AI 챗봇</span>
          {isFull && (
            <span className="text-[11px] text-zinc-400">
              재고 확인 / 발주 / 업무 질문을 도와드려요
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={resetChat}
            className="text-[11px] text-zinc-400 hover:text-zinc-700"
          >
            새 대화
          </button>
        </div>
      </div>

      {/* 메시지 영역 */}
      <div className="flex-1 px-4 py-3 space-y-2 overflow-y-auto text-sm">
        {messages.length === 0 && (
          <div className="text-xs text-zinc-400 text-center mt-6">
            {isFull
              ? '처음 오셨네요! "오늘 발주 상황 요약해줘"라고 물어보세요.'
              : "어떤 페이지에서도 바로 질문할 수 있어요 😄"}
          </div>
        )}

        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={
                "max-w-[80%] px-3 py-2 rounded-2xl whitespace-pre-wrap " +
                (m.role === "user"
                  ? "bg-black text-white rounded-br-sm"
                  : "bg-zinc-100 text-zinc-900 rounded-bl-sm")
              }
            >
              {m.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="text-xs text-zinc-400">
            답변을 작성 중이에요...
          </div>
        )}
      </div>

      {/* 입력 영역 */}
      <div className="border-t border-zinc-200 p-2 flex items-center gap-2">
        <input
          className="flex-1 text-xs border border-zinc-200 rounded-xl px-3 py-2 outline-none focus:ring-1 focus:ring-black"
          placeholder="질문을 입력하고 Enter를 눌러보세요"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="text-xs px-3 py-2 rounded-xl bg-black text-white disabled:bg-zinc-300 disabled:cursor-not-allowed"
        >
          전송
        </button>
      </div>
    </div>
  );
};