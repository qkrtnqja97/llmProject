// src/app/components/MainHeader.tsx
import React from "react";
import { BadgeCheck, Brain, Network } from "lucide-react";

export const MainHeader: React.FC = () => {
  return (
    <header className="h-14 border-b bg-white flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <span className="text-sm font-semibold text-zinc-900">
          Biz AI 업무 어시스턴트
        </span>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1 rounded-full border border-zinc-200 px-2 py-0.5 text-[11px] text-zinc-600 bg-zinc-50">
            <Brain className="w-3 h-3" />
            LLM 기반
          </span>
          <span className="inline-flex items-center gap-1 rounded-full border border-indigo-200 px-2 py-0.5 text-[11px] text-indigo-600 bg-indigo-50">
            <Network className="w-3 h-3" />
            RAG 문서 검색
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2 text-[11px] text-zinc-500">
        <BadgeCheck className="w-3 h-3" />
        <span>내부 데이터만 학습 · 안전한 사내용</span>
      </div>
    </header>
  );
};