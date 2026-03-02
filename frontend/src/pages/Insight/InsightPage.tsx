import React from "react";
// ✅ 전용 스타일 임포트
import styles from "./InsightPage.module.css";
// ✅ 공통 레이아웃 스타일 임포트 (상위 폴더 깊이에 맞춰 ../../ 확인)
import common from "../../app/styles/Global.module.css";

const InsightPage: React.FC = () => {
  return (
    <div className={common.pageSectionCard}>
      <h1 className={common.pageTitle}>비즈니스 인사이트</h1>
      <p className={common.pageText}>
        데이터를 분석하여 핵심 비즈니스 지표를 도출합니다.
      </p>

      <div className={styles.contentArea}>
        <span className={styles.statusIcon}>💡</span>
        <p className={common.pageText} style={{ marginTop: 0 }}>
          AI 분석 리포트를 준비 중입니다.
        </p>
      </div>
    </div>
  );
};

export default InsightPage;
