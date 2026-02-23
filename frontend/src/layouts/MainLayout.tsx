import React from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";

type MainLayoutProps = {
  loggedIn: boolean;
  onLoginClick: () => void;
};

const MainLayout: React.FC<MainLayoutProps> = ({
  loggedIn,
  onLoginClick,
}) => {
  return (
    <div className="min-h-screen bg-[#f5f5f7] flex">
      <Sidebar loggedIn={loggedIn} onLoginClick={onLoginClick} />

      <main className="flex-1 flex flex-col">
        <header className="h-14 border-b border-zinc-200 bg-white/80 backdrop-blur flex items-center justify-between px-6">
          <h1 className="text-sm font-semibold tracking-tight">
            biz ai · Operations Console
          </h1>
          <span className="text-[11px] text-zinc-400">
            베타 버전 · 팀 내 테스트용
          </span>
        </header>

        <div className="flex-1 p-6 overflow-y-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default MainLayout;