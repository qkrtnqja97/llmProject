/* src/context/ChatContext.tsx */
import { createContext, useContext, useState, ReactNode } from "react";
import { chatService } from "@services/chatService";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface ChatContextType {
  messages: Message[];
  sendMessage: (
    prompt: string,
    userId: string,
    onComplete?: () => void,
  ) => Promise<void>;
  lastQuestion: string;
  lastAnswer: string;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider = ({ children }: { children: ReactNode }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [lastQuestion, setLastQuestion] = useState("");
  const [lastAnswer, setLastAnswer] = useState("");

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
  };

  const sendMessage = async (
    prompt: string,
    userId: string,
    onComplete?: () => void,
  ) => {
    // 1. 사용자 질문 즉시 추가
    addMessage({ role: "user", content: prompt, timestamp: getNowTime() });

    try {
      // 2. 로딩용 빈 메시지 추가 (ChatPanel에서 점 3개 로딩바 표시용)
      addMessage({ role: "assistant", content: "", timestamp: getNowTime() });

      // 3. API 호출
      const data = await chatService.ask(prompt, userId);
      console.log("🔍 백엔드 수신 데이터 원본:", data);

      // 📍 [중요] [object Object] 방지를 위한 정밀 추출 로직
      let extractedText = "";

      if (typeof data === "string") {
        extractedText = data;
      } else if (data && typeof data === "object") {
        // 우선순위에 따라 필드 탐색
        // 백엔드 구조가 { answer: { final_answer: "..." } } 일 경우까지 대비
        const possibleContent =
          data.final_answer ||
          data.answer?.final_answer ||
          data.answer ||
          data.response ||
          data.data?.final_answer ||
          data.data?.answer ||
          data.data;

        if (typeof possibleContent === "string") {
          extractedText = possibleContent;
        } else if (
          typeof possibleContent === "object" &&
          possibleContent !== null
        ) {
          // 찾은 값이 또 객체라면 문자열로 강제 변환 (JSON 형태로 출력)
          extractedText = JSON.stringify(possibleContent, null, 2);
        } else {
          // 아무것도 해당 안 되면 전체 데이터 문자열화
          extractedText = JSON.stringify(data, null, 2);
        }
      } else {
        extractedText = String(data || "응답이 비어있습니다.");
      }

      // 최종적으로 [object Object] 문구 필터링 (최후의 보루)
      if (extractedText.includes("[object Object]")) {
        extractedText = JSON.stringify(data, null, 2);
      }

      // 4. 마지막 어시스턴트 메시지 업데이트
      setMessages((prev) => {
        const newMessages = [...prev];
        const lastIdx = newMessages.length - 1;
        if (newMessages[lastIdx] && newMessages[lastIdx].role === "assistant") {
          newMessages[lastIdx] = {
            ...newMessages[lastIdx],
            content: extractedText,
          };
        }
        return newMessages;
      });

      setLastAnswer(extractedText);

      if (onComplete) onComplete();
    } catch (error: any) {
      console.error("Chat API Error:", error);
      const errorMsg = "⚠️ 응답을 가져오는 중 오류가 발생했습니다.";

      setMessages((prev) => {
        const newMessages = [...prev];
        const lastIdx = newMessages.length - 1;
        if (newMessages[lastIdx]?.role === "assistant") {
          newMessages[lastIdx] = { ...newMessages[lastIdx], content: errorMsg };
        }
        return newMessages;
      });
      setLastAnswer(errorMsg);
      if (onComplete) onComplete();
    }
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        sendMessage,
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
