import * as Icon from "lucide-react";
import styles from "./QuoteManagePage.module.css";

const DUMMY_QUOTES = [
  {
    id: "QT-2603-001",
    client: "(주)테크솔루션",
    title: "서버 랙 및 쿨링 시스템",
    date: "2026-03-03",
    expiry: "2026-03-17",
    amount: 45000000,
    status: "sent",
  },
  {
    id: "QT-2603-002",
    client: "미래인더스트리",
    title: "정밀 센서 모듈 500ea",
    date: "2026-03-02",
    expiry: "2026-03-16",
    amount: 12500000,
    status: "converted",
  },
  {
    id: "QT-2602-089",
    client: "글로벌네트웍스",
    title: "네트워크 장비 교체건",
    date: "2026-02-15",
    expiry: "2026-03-01",
    amount: 8900000,
    status: "expired",
  },
  {
    id: "QT-2603-003",
    client: "한성정밀",
    title: "공정 자동화 라인 견적",
    date: "2026-03-03",
    expiry: "2026-03-31",
    amount: 128000000,
    status: "draft",
  },
];

const QuoteManagePage = () => {
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.titleGroup}>
          <h1>견적서 관리</h1>
        </div>
        <button
          className={styles.addBtn}
          style={{
            background: "var(--accent-color)",
            color: "white",
            padding: "10px 16px",
            borderRadius: "8px",
            border: "none",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            fontWeight: 700,
          }}
        >
          <Icon.FileText size={18} /> 신규 견적 작성
        </button>
      </header>

      <div className={styles.summaryRow}>
        <div className={styles.statCard}>
          <span className={styles.statLabel}>당월 견적 건수</span>
          <span className={styles.statValue}>42 건</span>
        </div>
        <div className={styles.statCard}>
          <span className={styles.statLabel}>견적 총액</span>
          <span className={styles.statValue}>582,400,000</span>
        </div>
        <div className={styles.statCard} style={{ borderLeftColor: "#3b82f6" }}>
          <span className={styles.statLabel}>진행 중 (Sent)</span>
          <span className={styles.statValue}>15 건</span>
        </div>
        <div className={styles.statCard} style={{ borderLeftColor: "#10b981" }}>
          <span className={styles.statLabel}>수주 전환율</span>
          <span className={styles.statValue}>68.4%</span>
        </div>
      </div>

      <div className={styles.tableCard}>
        <table className={styles.quoteTable}>
          <thead>
            <tr>
              <th>견적번호</th>
              <th>고객사</th>
              <th>견적명</th>
              <th>발행일</th>
              <th>유효기간</th>
              <th className={styles.amount}>금액</th>
              <th>상태</th>
              <th>작업</th>
            </tr>
          </thead>
          <tbody>
            {DUMMY_QUOTES.map((q) => (
              <tr key={q.id}>
                <td style={{ fontFamily: "JetBrains Mono", fontWeight: 600 }}>
                  {q.id}
                </td>
                <td style={{ fontWeight: 700 }}>{q.client}</td>
                <td>{q.title}</td>
                <td>{q.date}</td>
                <td>{q.expiry}</td>
                <td className={styles.amount}>￦{q.amount.toLocaleString()}</td>
                <td>
                  <span className={`${styles.statusBadge} ${styles[q.status]}`}>
                    {q.status === "sent"
                      ? "발송완료"
                      : q.status === "converted"
                        ? "수주전환"
                        : q.status === "expired"
                          ? "기간만료"
                          : "임시저장"}
                  </span>
                </td>
                <td>
                  {q.status === "sent" && (
                    <button className={styles.convertBtn}>수주전환</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default QuoteManagePage;
