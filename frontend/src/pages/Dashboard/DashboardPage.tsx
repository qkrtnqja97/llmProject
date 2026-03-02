import React from "react";
import styles from "./DashboardPage.module.css";
import common from "../../app/styles/Global.module.css";

const DashboardPage: React.FC = () => {
  return (
    <div className={common.pageSectionCard}>
      <h1 className={common.pageTitle}>운영 대시보드</h1>
      <div className={styles.contentArea}>
        <span className={styles.statusIcon}>📊</span>
        <p className={common.pageText}>
          실시간 통계 및 데이터를 준비 중입니다.
        </p>
      </div>
    </div>
  );
};

export default DashboardPage;
