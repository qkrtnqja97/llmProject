import React from "react";
import styles from "./TaskPage.module.css";
import common from "../../app/styles/Global.module.css";

const TaskPage: React.FC = () => {
  return (
    <div className={common.pageSectionCard}>
      <h3 className={common.pageTitle}>📝 업무 작성</h3>
      <p className={common.pageText}>수행한 업무 내용을 상세히 기록하세요.</p>

      <form className={styles.form}>
        <div className={styles.fieldGroup}>
          <label className={styles.label}>업무 제목</label>
          <input className={styles.input} placeholder="제목을 입력하세요" />
        </div>

        <div className={styles.fieldGroup}>
          <label className={styles.label}>내용</label>
          <textarea
            className={`${styles.input} ${styles.textarea}`}
            placeholder="상세 내용을 입력하세요"
          />
        </div>

        <button type="submit" className={styles.saveBtn}>
          작업 저장
        </button>
      </form>
    </div>
  );
};

export default TaskPage;
