import React, { createContext, useContext, useState, useCallback } from "react";
import { chatApi } from "../services/api";
import type { ChatMessage } from "../shared/types/chat";

interface ChatContextType {
  messages: ChatMessage[];
  isSending: boolean;
  sendMessage: (text: string) => Promise<void>;
  clearMessages: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);

  const sendMessage = useCallback(async (text: string) => {
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsSending(true);

    try {
      // 우선은 목업 함수를 사용하도록 설정 (필요시 chatApi.sendMessage로 교체)
      const answer = await chatApi.mockSendMessage(text);

      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: answer,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      console.error("Chat Error:", error);
    } finally {
      setIsSending(false);
    }
  }, []);

  const clearMessages = () => setMessages([]);

  return (
    <ChatContext.Provider
      value={{ messages, isSending, sendMessage, clearMessages }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) throw new Error("useChat must be used within ChatProvider");
  return context;
};
