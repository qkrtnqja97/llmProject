// src/context/ChatContext.tsx
import React, { createContext, useContext, useState } from "react";
import type { ReactNode } from "react";  // ✅ 타입 전용 import

type ChatMessage = {
  id: number;
  role: "user" | "assistant";
  content: string;
};

type ChatContextValue = {
  messages: ChatMessage[];
  loading: boolean;
  sendMessage: (text: string) => Promise<void>;
  resetChat: () => void;
};

const ChatContext = createContext<ChatContextValue | undefined>(undefined);

// 👉 백엔드 주소 네 FastAPI에 맞게 수정
const API_URL = "http://localhost:8000/chat";

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;

    const userText = text.trim();

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: "user",
      content: userText,
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText }), // 백엔드 스펙에 맞게 키 이름 확인!
      });

      if (!res.ok) {
        throw new Error("API error");
      }

      const data = await res.json();

      const botMessage: ChatMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: data.answer ?? JSON.stringify(data),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error(error);
      const errorMessage: ChatMessage = {
        id: Date.now() + 2,
        role: "assistant",
        content: "⚠️ 서버 통신 중 오류가 발생했어요. 잠시 후 다시 시도해 주세요.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const resetChat = () => {
    setMessages([]);
  };

  const value: ChatContextValue = {
    messages,
    loading,
    sendMessage,
    resetChat,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export const useChat = () => {
  const ctx = useContext(ChatContext);
  if (!ctx) {
    throw new Error("useChat은 ChatProvider 안에서만 사용할 수 있습니다.");
  }
  return ctx;
};