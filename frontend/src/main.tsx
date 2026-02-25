// src/main.tsx
// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./index.css";

import { LayoutProvider } from "./app/providers/LayoutProviders";
import { AppLayout } from "./layouts/AppLayout";  // ✅ named import + 경로 수정

// 👇 ChatProvider import 추가
import { ChatProvider } from "./context/ChatContext";

const App = () => {
  return (
    <LayoutProvider>
      <AppLayout>
        <div>홈 화면</div>
      </AppLayout>
    </LayoutProvider>
  );
};

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ChatProvider>
        <App />
      </ChatProvider>
    </BrowserRouter>
  </React.StrictMode>
);