import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./LoginModal.module.css";
import { useAuth } from "@context/AuthContext";
import { userService } from "@services/userService";

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose }) => {
  const [empId, setEmpId] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) return;

    setIsLoading(true);
    try {
      const success = await login(empId, password);

      if (success) {
        // 📍 로그인 성공 후 사용자 설정 테마를 가져와 즉시 적용하는 로직이
        // 서비스 내부(userService)나 App.tsx의 전역 상태에 포함되어 있다면
        // 여기서 테마 깜빡임 없이 바로 목적지로 이동합니다.
        const settings = await userService.getSettings();
        const destination = settings?.startPage || "/home";

        onClose();
        navigate(destination);
      } else {
        alert("사원번호 또는 비밀번호를 확인해주세요.");
      }
    } catch (error) {
      console.error("Login failed:", error);
      alert("로그인 중 서버 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles["modal-overlay"]} onClick={onClose}>
      <div
        className={styles["modal-content"]}
        onClick={(e) => e.stopPropagation()}
      >
        <h2>Biz AI 로그인</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="사원번호"
            value={empId}
            onChange={(e) => setEmpId(e.target.value)}
            required
            autoComplete="username"
          />
          <input
            type="password"
            placeholder="비밀번호"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
          <button
            type="submit"
            className={styles["login-submit-btn"]}
            disabled={isLoading}
          >
            {isLoading ? "접속 중..." : "접속하기"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginModal;
