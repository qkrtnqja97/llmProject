// frontend/src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "./layouts/MainLayouts"; // 파일 이름이 MainLayouts.tsx라면 이렇게
import SearchPage from "./pages/SearchPage";
import NotesPage from "./pages/NotesPage";
import SettingsPage from "./pages/SettingPage";
import LoginPage from "./pages/LoginPage";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 메인 레이아웃 (사이드바 + 상단) */}
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/search" replace />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="notes" element={<NotesPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="login" element={<LoginPage />} />
        </Route>

        {/* 이상한 주소 → /search로 보내기 */}
        <Route path="*" element={<Navigate to="/search" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
