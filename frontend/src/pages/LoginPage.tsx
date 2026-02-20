import { useState } from "react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    alert(`(데모) 로그인 시도: ${email}`);
  }

  return (
    <div className="page page--center">
      <div className="login-card">
        <h2 className="login-card__title">로그인</h2>
        <p className="login-card__subtitle">
          LLM 프로젝트 대시보드를 사용하려면 로그인하세요.
        </p>

        <form onSubmit={onSubmit} className="login-card__form">
          <label className="login-card__field">
            <span>이메일</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </label>

          <label className="login-card__field">
            <span>비밀번호</span>
            <input
              type="password"
              value={pw}
              onChange={(e) => setPw(e.target.value)}
              placeholder="••••••••"
              required
            />
          </label>

          <button type="submit" className="login-card__button">
            로그인
          </button>

          <button type="button" className="login-card__ghost-button">
            회원가입이 필요하신가요?
          </button>
        </form>
      </div>
    </div>
  );
}
