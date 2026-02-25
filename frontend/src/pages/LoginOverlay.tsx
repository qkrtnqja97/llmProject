import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
// ✅ CSS Module 임포트
import styles from "./LoginOverlay.module.css";

const LoginOverlay: React.FC = () => {
  const { login, isLoading } = useAuth();
  const [empId, setEmpId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await login(empId, password);
    } catch (err: any) {
      setError(err.message || "로그인 정보가 올바르지 않습니다.");
    }
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.card}>
        <div className={styles.header}>
          {/* 로고 아이콘 스타일은 기존 인라인 혹은 CSS에 추가 가능 */}
          <div
            style={{
              backgroundColor: "#111827",
              color: "white",
              width: "48px",
              height: "48px",
              borderRadius: "16px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 16px",
              fontWeight: "bold",
              fontSize: "20px",
            }}
          >
            AI
          </div>
          <h2 className={styles.title}>Biz AI Console</h2>
          <p className={styles.subtitle}>사내 계정으로 로그인이 필요합니다.</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label>사원번호</label>
            <input
              type="text"
              placeholder="사원번호를 입력하세요"
              value={empId}
              onChange={(e) => setEmpId(e.target.value)}
              required
            />
          </div>

          <div className={styles.field}>
            <label>비밀번호</label>
            <input
              type="password"
              placeholder="비밀번호를 입력하세요"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <p
              style={{
                color: "#ef4444",
                fontSize: "12px",
                fontWeight: "500",
                margin: "4px 0",
              }}
            >
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className={styles.loginBtn}
          >
            {isLoading ? "인증 중..." : "접속하기"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginOverlay;
