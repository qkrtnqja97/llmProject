// src/app/components/ChatAndDashboard.tsx
import React from "react";
import { ChatPanel } from "./ChatbotPanel";
import { DashboardPanel } from "./DashboardPannelCalendar";

export const ChatAndDashboard: React.FC = () => {
  return (
    <div className="h-full grid grid-cols-1 xl:grid-cols-[minmax(0,2.1fr)_minmax(320px,1fr)] gap-4">
      {/* Left: Chat */}
      <ChatPanel />

      {/* Right: Dashboard (인사이트 + 캘린더) */}
      <DashboardPanel />
    </div>
  );
};