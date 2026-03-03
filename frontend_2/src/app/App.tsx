// src/app/App.tsx
import { useLayoutEffect } from "react";
import { RouterProvider } from "react-router-dom";
import { router } from "@routes/index";
import { AuthProvider, useAuth } from "@context/AuthContext";
import { ChatProvider } from "@context/ChatContext";

const AppContent = () => {
  const { isInitialized } = useAuth();

  // 📍 렌더링 전 동기적으로 테마 상태를 한 번 더 체크 (안전장치)
  useLayoutEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    const validThemes = ["navy", "gray", "sand"];
    const themeToApply =
      savedTheme && validThemes.includes(savedTheme) ? savedTheme : "navy";

    document.documentElement.setAttribute("data-theme", themeToApply);

    // 초기 로딩 시 적용했던 인라인 배경색 스타일 제거 (CSS 변수가 우선되도록)
    document.documentElement.style.removeProperty("background-color");

    if (themeToApply !== savedTheme) {
      localStorage.setItem("theme", themeToApply);
    }
  }, []);
  if (!isInitialized) return null;

  return <RouterProvider router={router} />;
};

function App() {
  return (
    <AuthProvider>
      <ChatProvider>
        <AppContent />
      </ChatProvider>
    </AuthProvider>
  );
}

export default App;
