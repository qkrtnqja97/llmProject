// frontend/src/components/ChatWindow.tsx

import React, { useState } from "react";
import { askLLM, searchWorkspace } from "../services/api";

type Role = "user" | "assistant";

interface Message {
  id: string;
  role: Role;
  content: string;
  created_at: string;
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchLoading, setSearchLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userText = input.trim();

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: userText,
      created_at: new Date().toISOString(),
    };

    const next = [...messages, userMsg];
    setMessages(next);
    setInput("");
    setLoading(true);

    try {
      const res = await askLLM(userText, "auto");

      const aiMsg: Message = {
        id: Date.now().toString() + "-ai",
        role: "assistant",
        content: res.answer, // 백엔드에서 answer로 보내줌
        created_at: new Date().toISOString(),
      };

      setMessages([...next, aiMsg]);

      // RAG 검색 결과(참고 문서)도 같이 저장
      setSearchResults(res.sources || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    try {
      const results = await searchWorkspace(searchQuery.trim());
      setSearchResults(results);
    } catch (e) {
      console.error(e);
    } finally {
      setSearchLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full p-4 gap-4">
      {/* 상단 검색 바 */}
      <div className="flex gap-2 mb-2">
        <input
          className="flex-1 border rounded-xl px-3 py-2 text-sm"
          placeholder="문서·회의록 내용 검색..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSearch();
          }}
        />
        <button
          onClick={handleSearch}
          className="bg-black text-white px-4 rounded-xl text-sm"
          disabled={searchLoading}
        >
          {searchLoading ? "검색 중..." : "검색"}
        </button>
      </div>

      {/* 채팅 영역 */}
      <div className="flex-1 flex gap-4 min-h-0">
        {/* 왼쪽: 채팅창 */}
        <div className="flex-1 flex flex-col bg-white rounded-3xl shadow p-4">
          <div className="flex-1 overflow-y-auto space-y-3 mb-3">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`max-w-[70%] px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-black text-white ml-auto"
                    : "bg-zinc-100 text-black"
                }`}
              >
                {msg.content}
              </div>
            ))}
            {loading && (
              <div className="text-xs text-zinc-400">모델이 생각 중... 🧠</div>
            )}
          </div>

          {/* 입력창 */}
          <div className="flex gap-2">
            <input
              className="flex-1 border rounded-xl px-3 py-2 text-sm"
              placeholder="메시지를 입력하세요..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <button
              onClick={handleSend}
              className="bg-black text-white px-4 rounded-xl text-sm"
              disabled={loading || !input.trim()}
            >
              전송
            </button>
          </div>
        </div>

        {/* 오른쪽: RAG 검색 결과 패널 */}
        <div className="w-[300px] bg-white rounded-3xl shadow p-4 text-xs">
          <div className="font-semibold mb-2">참고 문서</div>
          {searchResults.length === 0 && (
            <div className="text-zinc-400">
              검색 결과가 없습니다. 위에서 키워드를 입력해 보세요.
            </div>
          )}
          <div className="space-y-2">
            {searchResults.map((r: any) => (
              <div
                key={r.id}
                className="border border-zinc-100 rounded-2xl p-2"
              >
                <div className="font-medium mb-1">{r.title}</div>
                <div className="text-zinc-500 line-clamp-3">{r.snippet}</div>
                {typeof r.score === "number" && (
                  <div className="text-[10px] text-zinc-400 mt-1">
                    score: {r.score.toFixed(3)}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}