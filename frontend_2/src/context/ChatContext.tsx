/* src/context/ChatContext.tsx */
import { createContext, useContext, useState, ReactNode, useRef } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  isStopped?: boolean; // 중단 상태를 위한 속성
}

interface ChatContextType {
  messages: Message[];
  addMessage: (msg: Message) => void;
  updateLastAssistantMessage: (chunk: string) => void;
  simulateStreaming: (question: string, onComplete?: () => void) => void;
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

  // 메시지 추가 함수
  const addMessage = (msg: Message) => {
    const timestamp = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
    const msgWithTime = { ...msg, timestamp: msg.timestamp || timestamp };

    setMessages((prev) => [...prev, msgWithTime]);

    if (msgWithTime.role === "user") {
      setLastQuestion(msgWithTime.content);
      setLastAnswer("");
    }
    if (msgWithTime.role === "assistant") {
      setLastAnswer(msgWithTime.content);
    }
  };

  // 마지막 어시스턴트 메시지에 텍스트 조각(chunk)을 추가하는 함수
  const updateLastAssistantMessage = (chunk: string) => {
    setMessages((prev) => {
      const lastMsg = prev[prev.length - 1];
      if (lastMsg && lastMsg.role === "assistant") {
        const updatedContent = lastMsg.content + chunk;
        return [...prev.slice(0, -1), { ...lastMsg, content: updatedContent }];
      } else {
        // 어시스턴트 메시지가 없으면 새로 생성
        const newMsg: Message = {
          role: "assistant",
          content: chunk,
          timestamp: new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
        };
        return [...prev, newMsg];
      }
    });
    // 최신 답변 상태 업데이트
    setLastAnswer((prev) => prev + chunk);
  };

  /**
   * 스트리밍 중지 함수
   * 인터벌을 제거하고 마지막 메시지에 중단 표시(isStopped)를 남깁니다.
   */
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
   * [임시 코드] 타이핑 효과 테스트를 위한 함수
   */
  const simulateStreaming = (question: string, onComplete?: () => void) => {
    // 이미 실행 중인 스트리밍이 있다면 먼저 중단
    if (typingIntervalRef.current) {
      clearInterval(typingIntervalRef.current);
    }

    const longText = `[테스트 응답 시작] 요청하신 "${question}"에 대한 긴 답변입니다. 
    이 문장은 타이핑 효과 및 중단 기능을 테스트하기 위해 생성되었습니다. 
    인공지능 시스템이 실시간으로 데이터를 처리하고 문장을 생성하는 과정을 시각적으로 확인하실 수 있습니다. 
    Smart Work 시스템의 채팅 인터페이스는 사용자의 입력에 즉각적으로 반응하며, 
    긴 문장이 생성될 때도 레이아웃이 깨지지 않고 자연스럽게 스크롤되도록 설계되었습니다. 
    현재 적용된 라이트/다크 모드 테마가 말풍선 배경과 텍스트 컬러에 정상적으로 반영되는지도 
    함께 확인해 보시기 바랍니다. 
    테스트가 완료되면 이 임시 로직을 제거하고 실제 백엔드 API 스트리밍과 연결하시면 됩니다. [테스트 끝]`;

    // 1. 먼저 빈 Assistant 메시지 추가하여 응답 시작 알림
    addMessage({ role: "assistant", content: "", timestamp: "" });

    // 2. 글자 한 개씩 끊어서 업데이트 (인터벌 시작)
    let index = 0;
    const interval = setInterval(() => {
      if (index < longText.length) {
        // current 문자열 조각 전달
        const char = longText[index];
        updateLastAssistantMessage(char);
        index++;
      } else {
        // 전체 텍스트 출력 완료 시 종료
        if (typingIntervalRef.current) {
          clearInterval(typingIntervalRef.current);
          typingIntervalRef.current = null;
        }
        if (onComplete) onComplete();
      }
    }, 30);

    typingIntervalRef.current = interval;
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        addMessage,
        updateLastAssistantMessage,
        simulateStreaming,
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
