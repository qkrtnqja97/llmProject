// frontend/src/App.tsx

import React, { useState } from "react";
import LlmDashboard from "./pages/LlmDashboard";
import LoginOverlay from "./pages/LoginOverlay"; // 새로 만들 컴포넌트

const App: React.FC = () => {
  const [loggedIn, setLoggedIn] = useState(false);

  // 처음 켰을 때부터 로그인 모달 띄우고 싶으니까 true로 시작
  const [forceLogin, setForceLogin] = useState(true);

  const handleRequireLogin = () => {
    if (!loggedIn) {
      setForceLogin(true);
    }
  };

  const handleLogin = () => {
    setLoggedIn(true);
    setForceLogin(false);
  };

  return (
    <>
      {/* 항상 메인 페이지 렌더 → 뒤에 깔림 */}
      <LlmDashboard
        loggedIn={loggedIn}
        onRequireLogin={handleRequireLogin}
      />

      {/* 로그인 안 되어 있고, 모달 띄우기 상태일 때만 오버레이 */}
      {!loggedIn && forceLogin && (
        <LoginOverlay
          onLogin={handleLogin}
          onClose={() => setForceLogin(false)}
        />
      )}
    </>
  );
};

export default App;