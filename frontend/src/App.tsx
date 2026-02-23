// frontend/src/App.tsx
import React, { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import { CompanyProvider } from "./context/CompanyContext";
import MainLayout from "./layouts/MainLayout";

import HomePage from "./pages/HomePage";
import ChatbotPage from "./pages/ChatbotPage";
import DashboardPage from "./pages/DashboardPage";
import CompanyPage from "./pages/CompanyPage";
import LibraryPage from "./pages/LibraryPage";
import InsightPage from "./pages/InsightPage";
import LoginOverlay from "./pages/LoginOverlay";

const App: React.FC = () => {
  const [loggedIn, setLoggedIn] = useState(false);
  const [showLogin, setShowLogin] = useState(true); // 처음 켜면 로그인부터

  const handleLogin = () => {
    setLoggedIn(true);
    setShowLogin(false);
  };

  const handleLoginClick = () => {
    if (!loggedIn) setShowLogin(true);
  };

  return (
    <CompanyProvider>
      <BrowserRouter>
        <MainLayout loggedIn={loggedIn} onLoginClick={handleLoginClick} />
        <Routes>
          <Route
            element={
              <MainLayout
                loggedIn={loggedIn}
                onLoginClick={handleLoginClick}
              />
            }
          >
            <Route path="/" element={<HomePage />} />
            <Route path="/ai" element={<ChatbotPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/company" element={<CompanyPage />} />
            <Route path="/library" element={<LibraryPage />} />
            <Route path="/insights" element={<InsightPage />} />
          </Route>
        </Routes>

        {!loggedIn && showLogin && (
          <LoginOverlay
            onLogin={handleLogin}
            onClose={() => setShowLogin(false)}
          />
        )}
      </BrowserRouter>
    </CompanyProvider>
  );
};

export default App;