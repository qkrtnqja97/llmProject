// import React, { useState, type KeyboardEvent, type FormEvent } from "react";

// type ChatMessage = {
//   id: number;
//   role: "user" | "assistant";
//   content: string;
// };

// const ChatbotPanel: React.FC = () => {
//   const [messages, setMessages] = useState<ChatMessage[]>([
//     {
//       id: 1,
//       role: "assistant",
//       content:
//         "안녕하세요 👋 biz ai 어시스턴트입니다.\n재고, 발주, 회의록 등 업로드된 문서 기반으로 도와드릴게요.",
//     },
//   ]);
//   const [input, setInput] = useState("");
//   const [loading, setLoading] = useState(false);

//   const sendMessage = async (e?: FormEvent) => {
//     if (e) e.preventDefault();
//     const trimmed = input.trim();
//     if (!trimmed || loading) return;

//     const userMsg: ChatMessage = {
//       id: Date.now(),
//       role: "user",
//       content: trimmed,
//     };

//     setMessages((prev) => [...prev, userMsg]);
//     setInput("");
//     setLoading(true);

//     try {
//       const res = await fetch("http://127.0.0.1:8000/api/chat", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ question: trimmed, mode: "auto" }),
//       });

//       if (!res.ok) throw new Error("API error");

//       const data = await res.json();

//       const botMsg: ChatMessage = {
//         id: Date.now() + 1,
//         role: "assistant",
//         content:
//           (data.answer as string) ??
//           "답변을 가져오지 못했어요. 잠시 후 다시 시도해 주세요.",
//       };

//       setMessages((prev) => [...prev, botMsg]);
//     } catch (err) {
//       console.error(err);
//       setMessages((prev) => [
//         ...prev,
//         {
//           id: Date.now() + 2,
//           role: "assistant",
//           content:
//             "서버와 통신 중 오류가 발생했어요. 백엔드 상태를 한 번 확인해 주세요 😢",
//         },
//       ]);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
//     if (e.key === "Enter" && !e.shiftKey) {
//       e.preventDefault();
//       sendMessage();
//     }
//   };

//   return (
//     <div className="bg-white rounded-3xl shadow-md p-6 flex flex-col max-w-3xl">
//       <div className="flex items-center justify-between mb-4">
//         <div>
//           <h2 className="text-sm font-semibold">AI 어시스턴트</h2>
//           <p className="text-[11px] text-zinc-500 mt-1">
//             회사 문서와 데이터를 기반으로 질문에 답변합니다.
//           </p>
//         </div>
//         <span className="text-[10px] px-2 py-1 rounded-full bg-emerald-50 text-emerald-700">
//           {loading ? "Thinking..." : "Online"}
//         </span>
//       </div>

//       {/* 메시지 영역 */}
//       <div className="h-72 border rounded-2xl p-3 mb-4 overflow-y-auto space-y-2 text-sm bg-zinc-50">
//         {messages.map((m) => (
//           <div
//             key={m.id}
//             className={`flex ${
//               m.role === "user" ? "justify-end" : "justify-start"
//             }`}
//           >
//             <div
//               className={`max-w-[80%] whitespace-pre-wrap px-4 py-2 rounded-2xl text-xs ${
//                 m.role === "user"
//                   ? "bg-zinc-900 text-white rounded-br-sm"
//                   : "bg-white text-zinc-900 rounded-bl-sm border"
//               }`}
//             >
//               {m.content}
//             </div>
//           </div>
//         ))}
//         {loading && (
//           <div className="flex justify-start">
//             <div className="bg-white border text-zinc-500 text-xs px-3 py-2 rounded-2xl rounded-bl-sm">
//               답변 생성 중이에요… 💭
//             </div>
//           </div>
//         )}
//       </div>

//       {/* 입력 영역 */}
//       <form
//         onSubmit={sendMessage}
//         className="flex gap-2 items-center text-xs md:text-sm"
//       >
//         <input
//           className="flex-1 bg-white border rounded-xl px-3 py-2 outline-none focus:ring-1 focus:ring-zinc-900"
//           placeholder="예) 다음 주까지 필요한 베어링 발주 수량 계산해줘"
//           value={input}
//           onChange={(e) => setInput(e.target.value)}
//           onKeyDown={handleKeyDown}
//         />
//         <button
//           type="submit"
//           disabled={loading}
//           className="px-4 py-2 rounded-xl bg-zinc-900 text-white font-medium disabled:opacity-50"
//         >
//           {loading ? "전송 중..." : "↩︎ 보내기"}
//         </button>
//       </form>
//     </div>
//   );
// };

// export default ChatbotPanel;

// src/app/components/ChatPanel.tsx
import React, { useState } from "react";
import { Send, Sparkles, Box, FileText, Users } from "lucide-react";

export const ChatPanel: React.FC = () => {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    // TODO: 여기에 LLM API 호출
    console.log("질문:", input);
    setInput("");
  };

  return (
    <section className="bg-white rounded-3xl shadow-sm border flex flex-col h-full">
      {/* 상단 */}
      <div className="px-5 py-4 border-b flex items-center justify-between">
        <div>
          <div className="text-sm font-semibold">AI 업무 검색</div>
          <div className="text-xs text-zinc-500">
            재고, 발주, 일정, 문서까지 자연어로 한 번에 물어보세요.
          </div>
        </div>
        <div className="flex items-center gap-1 text-[11px] text-indigo-600 bg-indigo-50 border border-indigo-100 rounded-full px-2 py-0.5">
          <Sparkles className="w-3 h-3" />
          <span>업무 특화 프롬프트 적용</span>
        </div>
      </div>

      {/* 채팅 내용 영역 (지금은 비어있는 예시) */}
      <div className="flex-1 overflow-auto px-5 py-4 space-y-3 text-sm text-zinc-600">
        <div className="text-xs text-zinc-400">
          아직 대화가 없습니다. 아래 예시를 눌러 시작해보세요.
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <QuickPrompt
            icon={<Box className="w-4 h-4" />}
            text="재고가 부족한 상품만 보여줘"
          />
          <QuickPrompt
            icon={<FileText className="w-4 h-4" />}
            text="오늘 남은 업무를 체크리스트로 정리해줘"
          />
          <QuickPrompt
            icon={<Users className="w-4 h-4" />}
            text="A상사와 최근 발주 내역 요약해줘"
          />
        </div>
      </div>

      {/* 입력창 */}
      <form onSubmit={handleSubmit} className="px-5 pb-4 pt-2">
        <div className="rounded-2xl border bg-zinc-50 px-3 py-2 flex items-center gap-2">
          <input
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-zinc-400"
            placeholder="사내 문서, 재고, 발주, 일정 등 무엇이든 물어보세요."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            type="submit"
            className="p-1.5 rounded-full bg-black text-white hover:opacity-90 disabled:opacity-40"
            disabled={!input.trim()}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <div className="mt-1 text-[10px] text-zinc-400">
          이 채팅은 검색 기록에 저장되어 나중에 다시 확인할 수 있어요.
        </div>
      </form>
    </section>
  );
};

type QuickPromptProps = {
  icon: React.ReactNode;
  text: string;
};

const QuickPrompt: React.FC<QuickPromptProps> = ({ icon, text }) => {
  return (
    <button className="flex items-center gap-2 text-xs px-3 py-2 rounded-2xl border border-zinc-100 hover:bg-zinc-50 text-left">
      <span className="shrink-0 text-zinc-500">{icon}</span>
      <span className="line-clamp-2">{text}</span>
    </button>
  );
};