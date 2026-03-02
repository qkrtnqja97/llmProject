import React from "react";
import styles from "./HistoryPage.module.css";
import common from "../../app/styles/Global.module.css";

const HistoryPage: React.FC = () => {
  const records = [
    { id: 1, query: "2024년 1분기 매출 보고서 요약해줘", date: "2시간 전" },
    { id: 2, query: "재고 부족 품목 리스트 뽑아줘", date: "어제" },
  ];

  return (
    <div className={common.pageSectionCard}>
      <h3 className={common.pageTitle}>📜 검색 기록</h3>
      <p className={common.pageText}>
        AI와 대화한 과거 이력을 확인하고 다시 질문하세요.
      </p>

      <div className={styles.list}>
        {records.map((rec) => (
          <div key={rec.id} className={styles.historyItem}>
            <div className={styles.queryInfo}>
              <span className={styles.queryText}>{rec.query}</span>
              <span className={styles.date}>{rec.date}</span>
            </div>
            <button className={styles.reBtn}>🔄</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HistoryPage;
