// frontend/src/pages/LlmDashboard.tsx

import React from "react";

type LlmDashboardProps = {
  loggedIn: boolean;          // 로그인 여부
  onRequireLogin: () => void; // 로그인 필요 시 호출 (지금은 로그인 모달 띄우는 용도)
};

// 메인 랜딩 페이지 (기업 홈페이지 느낌)
const LlmDashboard: React.FC<LlmDashboardProps> = ({
  loggedIn,
  onRequireLogin,
}) => {
  return (
    <div className="bg-[#000510] text-white min-h-screen font-sans">
      {/* 1. 네비게이션 바 */}
      <nav className="flex justify-between items-center px-10 py-5 fixed w-full z-50 bg-black/20 backdrop-blur-md border-b border-white/5">
        <div className="text-2xl font-bold tracking-tighter text-blue-500 italic">
          MEMS
        </div>

        <div className="hidden md:flex space-x-8 text-sm uppercase tracking-widest text-gray-300">
          <a href="#" className="hover:text-blue-400 transition-colors">
            회사소개
          </a>
          <a href="#" className="hover:text-blue-400 transition-colors">
            기술소개
          </a>
          <a href="#" className="hover:text-blue-400 transition-colors">
            제품분야
          </a>
          <a href="#" className="hover:text-blue-400 transition-colors">
            서비스
          </a>
        </div>

        <div className="flex items-center gap-6">
          <div className="text-xs space-x-2">
            <span className="text-blue-500 font-bold cursor-pointer">KR</span>
            <span className="text-gray-500 cursor-pointer hover:text-gray-300 transition-colors">
              EN
            </span>
          </div>

          {/* 로그인 상태에 따라 버튼 텍스트만 변경 */}
          <button
            onClick={onRequireLogin}
            className="px-5 py-2 bg-blue-600 rounded-full text-sm font-bold hover:bg-blue-500 transition-all shadow-lg shadow-blue-500/20"
          >
            {loggedIn ? "Dashboard" : "Login"}
          </button>
        </div>
      </nav>

      {/* 2. 히어로 섹션 */}
      <section className="relative h-screen flex flex-col items-center justify-center overflow-hidden">
        {/* 블러 라이트 */}
        <div className="absolute w-[600px] h-[600px] bg-blue-600 rounded-full blur-[120px] opacity-20 animate-pulse" />

        <div className="relative z-10 text-center space-y-6 px-4">
          <h3 className="text-blue-400 tracking-[0.3em] font-semibold text-xl uppercase">
            Future Tech
          </h3>
          <h1 className="text-5xl md:text-8xl font-bold leading-tight tracking-tighter">
            미시 세계로의 초대
          </h1>
          <p className="max-w-2xl mx-auto text-gray-400 text-lg md:text-xl leading-relaxed">
            MEMS는 반도체 제조 기술을 기반으로 하며, 미세한 구조물과
            <br className="hidden md:block" />
            전자 회로를 단일 칩 위에 통합하는 혁신을 주도합니다.
          </p>
          <button className="mt-8 px-10 py-4 border border-blue-500 text-blue-500 hover:bg-blue-500 hover:text-white transition-all rounded-full font-bold text-lg">
            Learn More +
          </button>
        </div>
      </section>

      {/* 3. 상세 설명 섹션 */}
      <section className="py-24 px-10 grid md:grid-cols-2 gap-16 items-center bg-white text-black">
        <div className="rounded-3xl overflow-hidden shadow-2xl transform hover:scale-[1.02] transition-transform duration-500">
          <img
            src="https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=1000"
            alt="Wafer Technology"
            className="w-full h-full object-cover"
          />
        </div>

        <div className="space-y-8">
          <h2 className="text-4xl md:text-5xl font-extrabold leading-tight">
            MEMS,
            <br />
            <span className="text-blue-600 underline underline-offset-8">
              세상을 변화시키다
            </span>
          </h2>
          <p className="text-gray-600 text-lg leading-relaxed">
            반도체와 MEMS 기술의 선구자로서, 우리는 미세한 차이가 만들어내는
            거대한 변화를 믿습니다. 정밀도와 혁신을 통해 당신의 비전을 현실로
            만들어 드립니다.
          </p>
          <div className="flex gap-4">
            <button className="bg-blue-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-blue-700 transition-colors">
              Products View
            </button>
            <button className="border border-gray-300 text-gray-600 px-8 py-3 rounded-xl font-bold hover:bg-gray-50 transition-colors">
              Contact Us
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LlmDashboard;