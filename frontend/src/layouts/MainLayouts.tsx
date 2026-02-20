import logo from "../assets/logo.png";
import { NavLink, Outlet, useLocation } from "react-router-dom";

const menuItems = [
  { to: "/search", label: "검색", icon: "🔍" },
  { to: "/notes", label: "노트", icon: "📝" },
  { to: "/settings", label: "설정", icon: "⚙️" },
];

export default function MainLayout() {
  const location = useLocation();

  return (
    <div className="app-root">
      {/* 왼쪽 사이드바 */}
      <aside className="sidebar">
        <div className="sidebar__logo">
       <img src={logo} alt="logo" className="sidebar__logo-img" />
<span className="sidebar__logo-text">LLM Project</span>

        </div>

        <nav className="sidebar__nav">
          {menuItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                "sidebar__nav-item" + (isActive ? " sidebar__nav-item--active" : "")
              }
            >
              <span className="sidebar__nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar__bottom">
          <NavLink
            to="/login"
            className={({ isActive }) =>
              "sidebar__nav-item sidebar__nav-item--ghost" +
              (isActive ? " sidebar__nav-item--active-ghost" : "")
            }
          >
            <span className="sidebar__nav-icon">👤</span>
            <span>로그인</span>
          </NavLink>

          <div className="sidebar__footer">
            <div className="sidebar__user-circle">S</div>
            <div className="sidebar__user-info">
              <div className="sidebar__user-name">수연</div>
              <div className="sidebar__user-sub">AI Front Test</div>
            </div>
          </div>
        </div>
      </aside>

      {/* 오른쪽 메인 영역 */}
      <main className="main">
        {/* 상단 바 (페이지 제목 같은 느낌) */}
        <header className="main__header">
          <div className="main__title">
            {location.pathname.startsWith("/search") && "검색"}
            {location.pathname.startsWith("/notes") && "노트"}
            {location.pathname.startsWith("/settings") && "설정"}
            {location.pathname.startsWith("/login") && "로그인"}
          </div>
        </header>

        {/* 실제 페이지 내용 */}
        <section className="main__content">
          <Outlet />
        </section>
      </main>
    </div>
  );
}
