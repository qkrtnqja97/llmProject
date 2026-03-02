import React from "react";
import styles from "./ContactPage.module.css";
import common from "../../app/styles/Global.module.css";

const ContactPage: React.FC = () => {
  return (
    <div className={common.pageSectionCard}>
      <h3 className={common.pageTitle}>👥 비즈니스 연락처</h3>
      <p className={common.pageText}>협력사 및 내부 담당자 목록입니다.</p>

      <div className={styles.gridContainer}>
        {[1, 2, 3].map((i) => (
          <div key={i} className={styles.contactCard}>
            <p className={styles.name}>담당자 {i}</p>
            <p className={styles.info}>기술지원팀</p>
            <p className={styles.info}>010-0000-000{i}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ContactPage;
