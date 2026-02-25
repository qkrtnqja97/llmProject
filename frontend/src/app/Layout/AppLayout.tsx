// // src/app/layouts/AppLayout.tsx
// import React, { useState } from "react";
// import { Sidebar } from "../../components/Sidebar";
// import { LayoutSettings } from "../../components/LayoutSettings";

// const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
//   const [settingsOpen, setSettingsOpen] = useState(false);
//   const [loggedIn, setLoggedIn] = useState(false); // ✅ 로그인 상태

//   return (
//     <div className="min-h-screen flex bg-[#f5f5f7]">
//       <Sidebar
//         loggedIn={loggedIn}
//         onLoginClick={() => setLoggedIn(true)}          // ✅ 버튼 누르면 로그인 처리
//         onOpenSettings={() => setSettingsOpen(true)}
//       />

//       <main className="flex-1 p-6">{children}</main>

//       {settingsOpen && (
//         <LayoutSettings onClose={() => setSettingsOpen(false)} />
//       )}
//     </div>
//   );
// };

// export default AppLayout;

// src/app/layouts/AppLayout.tsx
import React, { useState } from "react";
import { Sidebar } from "../components/Sidebar";
import { MainHeader } from "../components/MainHeader";
import { ChatAndDashboard } from "../components/ChatAndDashboard";

export const AppLayout: React.FC = () => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  return (
    <div className="min-h-screen flex bg-[#f5f5f7]">
      {/* Sidebar */}
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed((prev) => !prev)}
      />

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0">
        <MainHeader />
        <main className="flex-1 overflow-auto p-6">
          <ChatAndDashboard />
        </main>
      </div>
    </div>
  );
};