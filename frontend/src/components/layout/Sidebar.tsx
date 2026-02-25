import React from "react";
import { NavLink } from "react-router-dom";
import { useCompany } from "../../context/CompanyContext";
import { layoutStorage } from "../../shared/libs/layoutStorage";
import { useAuth } from "../../context/AuthContext";
// ✅ CSS Module 임포트
import styles from "./Sidebar.module.css";

const Sidebar: React.FC = () => {
  const { company } = useCompany();
  const { user, logout } = useAuth();
  const menu = layoutStorage.loadMenu();

  const handleLogout = () => {
    if (window.confirm("로그아웃 하시겠습니까?")) {
      logout();
    }
  };

  return (
    <aside className={styles.sidebar}>
      {/* 로고 섹션 */}
      <div className={styles.logo}>
        {company.logoUrl ? (
          <img src={company.logoUrl} alt="logo" className={styles.logoImg} />
        ) : (
          <div className={styles.logoBadge}>
            {company.name.slice(0, 2).toUpperCase()}
          </div>
        )}
        <span className={styles.logoText}>{company.name}</span>
      </div>

      {/* 메인 네비게이션 */}
      <nav className={styles.nav}>
        {menu
          .filter((m) => m.visible !== false)
          .map((item) => (
            <NavLink
              key={item.id}
              to={item.path}
              className={({ isActive }) =>
                `${styles.navItem} ${isActive ? styles.active : ""}`
              }
            >
              <span className={styles.navIcon}>
                {item.pinned ? "📌" : "📄"}
              </span>
              {item.label}
            </NavLink>
          ))}
      </nav>

      {/* 하단 설정 영역 */}
      <div className={styles.sidebarBottom}>
        <NavLink
          to="/company"
          className={({ isActive }) =>
            `${styles.navItemGhost} ${isActive ? styles.activeGhost : ""}`
          }
        >
          <span className={styles.navIcon}>⚙️</span>
          시스템 설정
        </NavLink>

        {/* ✅ 통합된 유저 섹션: 클릭 시 로그아웃 */}
        <button
          className={styles.sidebarFooter}
          onClick={handleLogout}
          title="클릭하여 로그아웃"
        >
          <div className={styles.userCircle}>
            {user?.name?.slice(0, 1) || "A"}
          </div>
          <div className={styles.userInfo}>
            <span className={styles.userName}>
              {user?.name || "Admin User"}
            </span>
            <span className={styles.userSub}>
              {user?.empId || "관리자 계정"}
            </span>
          </div>
          <span className={styles.logoutText}>로그아웃</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
