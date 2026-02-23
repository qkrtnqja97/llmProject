// frontend/src/pages/LoginPage.tsx
import React from "react";

interface LoginPageProps {
  onLogin: () => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-900 via-zinc-800 to-zinc-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white/95 rounded-3xl shadow-2xl p-8 space-y-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <div className="w-9 h-9 rounded-2xl bg-black text-white flex items-center justify-center text-sm">
              AI
            </div>
            <div>
              <p className="text-xs text-zinc-500">Enterprise Console</p>
              <p className="text-sm font-semibold tracking-tight">
                Operations AI Portal
              </p>
            </div>
          </div>
          <h1 className="text-lg font-semibold mt-4">
            사내 계정으로 로그인
          </h1>
          <p className="text-xs text-zinc-500 mt-1">
            재고/발주/회의록 데이터를 조회하고 AI Copilot을 사용할 수 있습니다.
          </p>
        </div>

        <div className="space-y-4 text-sm">
          <div className="space-y-1">
            <label className="text-xs text-zinc-600">이메일</label>
            <input
              type="email"
              className="w-full border rounded-xl px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-zinc-900"
              placeholder="name@company.com"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-zinc-600">비밀번호</label>
            <input
              type="password"
              className="w-full border rounded-xl px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-zinc-900"
              placeholder="••••••••"
            />
          </div>
          <div className="flex items-center justify-between text-[11px] text-zinc-500">
            <label className="flex items-center gap-1">
              <input type="checkbox" className="w-3 h-3" />
              <span>로그인 상태 유지</span>
            </label>
            <button className="hover:underline">비밀번호 찾기</button>
          </div>
        </div>

        <button
          onClick={onLogin}
          className="w-full bg-black text-white text-sm py-2.5 rounded-xl hover:opacity-90 transition"
        >
          로그인
        </button>

        <p className="text-[11px] text-zinc-400 text-center">
          외부 고객사는 담당자에게 계정 발급을 요청해주세요.
        </p>
      </div>
    </div>
  );
};

export default LoginPage;