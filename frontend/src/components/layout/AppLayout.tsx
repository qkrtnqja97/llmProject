import React from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Header from "./Header";
// ✅ CSS Module 임포트
import styles from "./AppLayout.module.css";

const AppLayout: React.FC = () => {
  return (
    <div className={styles.appRoot}>
      {/* 왼쪽 사이드바 */}
      <Sidebar />

      {/* 오른쪽 메인 영역 */}
      <div className={styles.main}>
        <Header />

        <main className={styles.content}>
          {/* 중앙 정렬 및 최대 너비를 유지하기 위한 컨테이너 */}
          <div className={styles.maxContainer}>
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
