import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom"; // 추가
import { useModal } from "@hooks/useModal";
import { useAuth } from "@context/AuthContext";
import LoginModal from "@components/modals/LoginModal";
import logoImg from "@assets/logo_1.png";
import nameImg from "@assets/name_1.png";
import styles from "./HomePage.module.css";

const HomePage: React.FC = () => {
  const { isOpen, open, close } = useModal();
  const { user, isInitialized } = useAuth();
  const navigate = useNavigate(); // 추가

  useEffect(() => {
    if (isInitialized) {
      if (!user) {
        open();
      } else {
        close();
        // 이미 로그인된 사용자가 /home에 들어왔을 때 시작 페이지 설정이 있다면 이동
        const destination = localStorage.getItem("startPage");
        const currentPath = window.location.pathname;
        if (
          user &&
          destination &&
          destination !== currentPath &&
          (currentPath === "/" || currentPath === "/home")
        ) {
          // navigate(destination);
        }
      }
    }
  }, [isInitialized, user, open, close, navigate]);

  if (!isInitialized) {
    return <div className={styles.loading}>인증 정보 로딩 중...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <div className={styles.mainLogoSection}>
          <img src={logoImg} alt="Logo Icon" className={styles.mainLogoIcon} />
          <img src={nameImg} alt="Smart Work" className={styles.mainNameImg} />
        </div>
        <p className={styles.subtitle}>
          {user
            ? `${user}님, 환영합니다! 오늘 어떤 업무를 도와드릴까요?`
            : "효율적인 업무 환경을 위한 AI 기반 스마트 솔루션"}
        </p>
        <button
          className={styles.startBtn}
          onClick={
            user
              ? () => {
                  const dest =
                    localStorage.getItem("startPage") || "/ai-search";
                  navigate(dest);
                }
              : open
          }
        >
          {user ? "업무 시작하기" : "로그인 후 이용하기"}
        </button>
      </div>

      <footer className={styles.footer}>
        © 2026 Smart Work Project. All rights reserved.
      </footer>

      <LoginModal isOpen={isOpen} onClose={close} />
    </div>
  );
};

export default HomePage;
