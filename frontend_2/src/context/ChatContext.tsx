/* src/context/ChatContext.tsx */
import { createContext, useContext, useState, ReactNode, useRef } from "react";
import { chatService } from "@services/chatService";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  isStopped?: boolean;
}

interface ChatContextType {
  messages: Message[];
  addMessage: (msg: Message) => void;
  updateLastAssistantMessage: (chunk: string) => void;
  sendMessage: (
    prompt: string,
    userId: string,
    onComplete?: () => void,
  ) => Promise<void>;
  stopStreaming: () => void;
  lastQuestion: string;
  lastAnswer: string;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider = ({ children }: { children: ReactNode }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [lastQuestion, setLastQuestion] = useState("");
  const [lastAnswer, setLastAnswer] = useState("");

  const typingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // 현재 시간 포맷팅 함수
  const getNowTime = () =>
    new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

  // 메시지 추가 함수
  const addMessage = (msg: Message) => {
    const msgWithTime = { ...msg, timestamp: msg.timestamp || getNowTime() };

    setMessages((prev) => [...prev, msgWithTime]);

    if (msgWithTime.role === "user") {
      setLastQuestion(msgWithTime.content);
      setLastAnswer("");
    }
    if (msgWithTime.role === "assistant") {
      setLastAnswer(msgWithTime.content);
    }
  };

  // 마지막 어시스턴트 메시지에 텍스트 조각을 추가하는 함수
  const updateLastAssistantMessage = (chunk: string) => {
    setMessages((prev) => {
      const lastMsg = prev[prev.length - 1];
      if (lastMsg && lastMsg.role === "assistant") {
        const updatedContent = lastMsg.content + chunk;
        return [...prev.slice(0, -1), { ...lastMsg, content: updatedContent }];
      } else {
        return [
          ...prev,
          { role: "assistant", content: chunk, timestamp: getNowTime() },
        ];
      }
    });
    setLastAnswer((prev) => prev + chunk);
  };

  // 스트리밍(출력) 중지 함수
  const stopStreaming = () => {
    if (typingIntervalRef.current) {
      clearInterval(typingIntervalRef.current);
      typingIntervalRef.current = null;

      setMessages((prev) => {
        const lastMsg = prev[prev.length - 1];
        if (lastMsg && lastMsg.role === "assistant") {
          return [...prev.slice(0, -1), { ...lastMsg, isStopped: true }];
        }
        return prev;
      });
    }
  };

  /**
   * 실제 AI API와 통신하여 메시지를 보내고 타이핑 효과를 구현하는 함수
   */
  const sendMessage = async (
    prompt: string,
    userId: string,
    onComplete?: () => void,
  ) => {
    // 1. 기존 동작 중인 타이핑이 있다면 중단
    if (typingIntervalRef.current) {
      clearInterval(typingIntervalRef.current);
    }

    // 2. 사용자 메시지 추가
    addMessage({ role: "user", content: prompt, timestamp: getNowTime() });

    try {
      // 3. 백엔드 API 호출
      const data = await chatService.ask(prompt, userId);
      const fullResponse = data.response;

      // 4. 어시스턴트 빈 메시지 시작
      addMessage({ role: "assistant", content: "", timestamp: getNowTime() });

      // 5. 타이핑 효과 시작 (글자별로 출력)
      let index = 0;
      const interval = setInterval(() => {
        if (index < fullResponse.length) {
          updateLastAssistantMessage(fullResponse[index]);
          index++;
        } else {
          if (typingIntervalRef.current) {
            clearInterval(typingIntervalRef.current);
            typingIntervalRef.current = null;
          }
          if (onComplete) onComplete();
        }
      }, 20); // 출력 속도 조절 (20ms)

      typingIntervalRef.current = interval;
    } catch (error) {
      console.error("Chat API Error:", error);
      addMessage({
        role: "assistant",
        content:
          "⚠️ 서버와 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        timestamp: getNowTime(),
      });
      if (onComplete) onComplete();
    }
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        addMessage,
        updateLastAssistantMessage,
        sendMessage, // ✅ simulateStreaming 대신 sendMessage 사용
        stopStreaming,
        lastQuestion,
        lastAnswer,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) throw new Error("useChat must be used within a ChatProvider");
  return context;
};
