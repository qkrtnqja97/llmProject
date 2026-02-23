import React, { useState, type KeyboardEvent, type FormEvent } from "react";

type ChatMessage = {
  id: number;
  role: "user" | "assistant";
  content: string;
};

const ChatbotPanel: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      role: "assistant",
      content:
        "안녕하세요 👋 biz ai 어시스턴트입니다.\n재고, 발주, 회의록 등 업로드된 문서 기반으로 도와드릴게요.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e?: FormEvent) => {
    if (e) e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMsg: ChatMessage = {
      id: Date.now(),
      role: "user",
      content: trimmed,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed, mode: "auto" }),
      });

      if (!res.ok) throw new Error("API error");

      const data = await res.json();

      const botMsg: ChatMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content:
          (data.answer as string) ??
          "답변을 가져오지 못했어요. 잠시 후 다시 시도해 주세요.",
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 2,
          role: "assistant",
          content:
            "서버와 통신 중 오류가 발생했어요. 백엔드 상태를 한 번 확인해 주세요 😢",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="bg-white rounded-3xl shadow-md p-6 flex flex-col max-w-3xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-sm font-semibold">AI 어시스턴트</h2>
          <p className="text-[11px] text-zinc-500 mt-1">
            회사 문서와 데이터를 기반으로 질문에 답변합니다.
          </p>
        </div>
        <span className="text-[10px] px-2 py-1 rounded-full bg-emerald-50 text-emerald-700">
          {loading ? "Thinking..." : "Online"}
        </span>
      </div>

      {/* 메시지 영역 */}
      <div className="h-72 border rounded-2xl p-3 mb-4 overflow-y-auto space-y-2 text-sm bg-zinc-50">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex ${
              m.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[80%] whitespace-pre-wrap px-4 py-2 rounded-2xl text-xs ${
                m.role === "user"
                  ? "bg-zinc-900 text-white rounded-br-sm"
                  : "bg-white text-zinc-900 rounded-bl-sm border"
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border text-zinc-500 text-xs px-3 py-2 rounded-2xl rounded-bl-sm">
              답변 생성 중이에요… 💭
            </div>
          </div>
        )}
      </div>

      {/* 입력 영역 */}
      <form
        onSubmit={sendMessage}
        className="flex gap-2 items-center text-xs md:text-sm"
      >
        <input
          className="flex-1 bg-white border rounded-xl px-3 py-2 outline-none focus:ring-1 focus:ring-zinc-900"
          placeholder="예) 다음 주까지 필요한 베어링 발주 수량 계산해줘"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-zinc-900 text-white font-medium disabled:opacity-50"
        >
          {loading ? "전송 중..." : "↩︎ 보내기"}
        </button>
      </form>
    </div>
  );
};

export default ChatbotPanel;