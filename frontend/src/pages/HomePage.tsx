// src/pages/HomePage.tsx
import React from "react";
import ChatWindow from "../components/ChatWindow";

const HomePage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* 상단: 풀 사이즈 챗봇 */}
      <div className="flex h-full min-h-screen items-center justify-center px-4">
        <div className="w-full max-w-4xl h-[70vh]">
          {/* ChatWindow는 full 전용이라 variant prop 안 줘도 돼 */}
          <ChatWindow />
        </div>
      </div>

      {/* 하단: 소개 섹션 */}
      <section className="bg-gradient-to-br from-[#0b1020] via-[#050816] to-[#05060a] text-white rounded-3xl px-10 py-10 shadow-sm">
        <p className="text-[11px] tracking-[0.3em] text-blue-300 mb-4">
          FUTURE TECH
        </p>
        <h1 className="text-4xl md:text-5xl font-bold mb-4">Biz AI</h1>
        <p className="text-sm md:text-base text-zinc-300 max-w-xl">
          AI 어시스턴트에게 자연어로 지시할 수 있는 Biz AI 콘솔입니다.
        </p>
        <div className="mt-6 flex flex-wrap gap-3 text-xs">
          <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10">
            RAG 기반 문서 검색
          </span>
          <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10">
            재고·발주 대시보드
          </span>
          <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10">
            회의록 인사이트
          </span>
        </div>
      </section>

      <section className="grid md:grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl p-4 shadow-sm">
          <h3 className="text-sm font-semibold mb-1">AI 어시스턴트</h3>
          <p className="text-xs text-zinc-500 mb-3">
            사내 문서를 연결한 챗봇으로, 업무 질문을 자연어로 처리합니다.
          </p>
          <p className="text-[11px] text-blue-600 font-medium">
            메뉴 &gt; AI 어시스턴트 에서 바로 사용 가능
          </p>
        </div>

        <div className="bg-white rounded-2xl p-4 shadow-sm">
          <h3 className="text-sm font-semibold mb-1">대시보드</h3>
          <p className="text-xs text-zinc-500 mb-3">
            부품 재고, 발주, 생산 회의 로그를 카드 형태로 한 눈에 확인하세요.
          </p>
          <p className="text-[11px] text-blue-600 font-medium">
            메뉴 &gt; 대시보드 에서 확인
          </p>
        </div>

        <div className="bg-white rounded-2xl p-4 shadow-sm">
          <h3 className="text-sm font-semibold mb-1">자료실·인사이트</h3>
          <p className="text-xs text-zinc-500 mb-3">
            문서를 업로드하고, 회의 요약·추세 분석 등 인사이트를 공유합니다.
          </p>
          <p className="text-[11px] text-blue-600 font-medium">
            메뉴 &gt; 자료실 / 인사이트
          </p>
        </div>
      </section>
    </div>
  );
};

export default HomePage;