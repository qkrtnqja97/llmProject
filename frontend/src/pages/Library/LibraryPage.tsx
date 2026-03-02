import React from "react";
import styles from "./LibraryPage.module.css";
import common from "../../app/styles/Global.module.css";

const LibraryPage: React.FC = () => {
  return (
    <div className={common.pageSectionCard}>
      <h3 className={common.pageTitle}>문서 자료실</h3>
      <p className={common.pageText}>업로드된 사내 주요 문서들을 관리합니다.</p>

      <div className={styles.listContainer}>
        <div className={styles.emptyState}>
          파일 목록을 불러오는 중입니다...
        </div>
      </div>
    </div>
  );
};

export default LibraryPage;
