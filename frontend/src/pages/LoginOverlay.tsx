import type { FormEvent } from "react";

interface LoginOverlayProps {
  onLogin: () => void;
  onClose: () => void;
}

export default function LoginOverlay({ onLogin }: LoginOverlayProps) {
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    // TODO: 나중에 실제 사원번호 검증 붙이면 여기에서
    onLogin();
  };

  return (
    <div
      className="
        fixed inset-0 z-50 
        flex items-center justify-center
        bg-black/40 backdrop-blur-md
      "
    >
      {/* 카드 */}
      <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-full bg-black text-white flex items-center justify-center text-sm font-semibold">
            AI
          </div>
          <div className="flex flex-col">
            <span className="text-[11px] text-zinc-500">
              Enterprise Console
            </span>
            <span className="text-sm font-semibold">
              Operations AI Portal
            </span>
          </div>
        </div>

        <h2 className="text-lg font-semibold mb-1">사내 계정으로 로그인</h2>
        <p className="text-[11px] text-zinc-500 mb-6">
          재고/발주/회의 데이터를 조회하고 AI Copilot을 사용할 수 있습니다.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 🔢 사원번호 입력 */}
          <div className="space-y-1">
            <label className="text-[11px] text-zinc-600">사원번호</label>
            <input
              className="w-full rounded-xl border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black"
              placeholder="예: 2026-0312"
            />
          </div>

          {/* 🔐 비밀번호 (원하면 나중에 제거 가능) */}
          <div className="space-y-1">
            <label className="text-[11px] text-zinc-600">비밀번호</label>
            <input
              type="password"
              className="w-full rounded-xl border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black"
              placeholder="사내 계정 비밀번호"
            />
          </div>

          <div className="flex items-center justify-between text-[11px] text-zinc-500">
            <label className="flex items-center gap-1">
              <input type="checkbox" className="w-3 h-3" />
              <span>로그인 상태 유지</span>
            </label>
            <button type="button" className="underline underline-offset-2">
              비밀번호 찾기
            </button>
          </div>

          <button
            type="submit"
            className="w-full mt-2 bg-black text-white py-2.5 rounded-2xl text-sm font-medium hover:opacity-90 transition"
          >
            로그인
          </button>
        </form>

        <p className="mt-4 text-[10px] text-zinc-400 text-center">
          외부 고객사는 담당자에게 계정 발급을 요청해 주세요.
        </p>
      </div>
    </div>
  );
}