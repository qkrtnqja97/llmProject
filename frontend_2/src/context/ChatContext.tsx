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

  const getNowTime = () =>
    new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

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

  const updateLastAssistantMessage = (chunk: string) => {
    setMessages((prev) => {
      if (prev.length === 0) return prev; // 방어 코드: 메시지가 없으면 중단

      const lastIdx = prev.length - 1;
      const lastMsg = prev[lastIdx];

      if (lastMsg && lastMsg.role === "assistant") {
        const updatedContent = lastMsg.content + chunk;
        const newMessages = [...prev];
        newMessages[lastIdx] = { ...lastMsg, content: updatedContent };
        return newMessages;
      }
      return prev;
    });
    setLastAnswer((prev) => prev + chunk);
  };

  const stopStreaming = () => {
    if (typingIntervalRef.current) {
      clearInterval(typingIntervalRef.current);
      typingIntervalRef.current = null;

      setMessages((prev) => {
        if (prev.length === 0) return prev;
        const lastIdx = prev.length - 1;
        const lastMsg = prev[lastIdx];
        if (lastMsg && lastMsg.role === "assistant") {
          const newMessages = [...prev];
          newMessages[lastIdx] = { ...lastMsg, isStopped: true };
          return newMessages;
        }
        return prev;
      });
    }
  };

  const sendMessage = async (
    prompt: string,
    userId: string,
    onComplete?: () => void,
  ) => {
    // 1. 기존 인터벌 확실히 제거
    if (typingIntervalRef.current) {
      clearInterval(typingIntervalRef.current);
      typingIntervalRef.current = null;
    }

    // 2. 유저 질문 추가
    addMessage({ role: "user", content: prompt, timestamp: getNowTime() });

    try {
      const data = await chatService.ask(prompt, userId);

      // 3. 데이터 추출 및 문자열 강제 변환 (방어 로직)
      let fullResponse = "";
      const rawData = data?.response || data?.data?.response;

      if (typeof rawData === "string") {
        fullResponse = rawData;
      } else if (typeof rawData === "object") {
        fullResponse = JSON.stringify(rawData); // 객체로 오면 문자열로 풀기
      } else {
        fullResponse = "응답 데이터 형식이 올바르지 않습니다.";
      }

      // 4. 빈 어시스턴트 말풍선 생성
      addMessage({ role: "assistant", content: "", timestamp: getNowTime() });

      // 5. 타이핑 효과 시작
      let index = 0;
      const interval = setInterval(() => {
        // fullResponse가 유효하고 index가 범위 내에 있을 때만 실행
        if (fullResponse && index < fullResponse.length) {
          updateLastAssistantMessage(fullResponse[index]);
          index++;
        } else {
          // 종료 처리
          clearInterval(interval);
          typingIntervalRef.current = null;
          if (onComplete) onComplete();
        }
      }, 20);

      typingIntervalRef.current = interval;
    } catch (error) {
      console.error("Chat API Error:", error);
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
        typingIntervalRef.current = null;
      }
      addMessage({
        role: "assistant",
        content: "⚠️ 서버 통신 오류가 발생했습니다.",
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
        sendMessage,
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
