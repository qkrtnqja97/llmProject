import * as Icon from "lucide-react";
import styles from "./OrderSoPage.module.css";

const DUMMY_SO = [
  {
    id: "SO-2603-042",
    client: "(주)테크솔루션",
    title: "데이터센터 쿨링 시스템",
    orderDate: "2026-03-03",
    dueDate: "2026-04-15",
    amount: 45000000,
    progress: 10,
    status: "생산대기",
  },
  {
    id: "SO-2602-115",
    client: "미래인더스트리",
    title: "정밀 센서 모듈 외 2건",
    orderDate: "2026-02-28",
    dueDate: "2026-03-10",
    amount: 12500000,
    progress: 85,
    status: "출고준비",
  },
  {
    id: "SO-2602-090",
    client: "현대건설기계",
    title: "유압 시스템 부품",
    orderDate: "2026-02-20",
    dueDate: "2026-03-05",
    amount: 33000000,
    progress: 100,
    status: "인도완료",
  },
];

const OrderSoPage = () => {
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1 style={{ fontSize: "1.75rem", fontWeight: 800 }}>
            수주 확정 현황
          </h1>
          <p style={{ color: "var(--text-sub)" }}>
            진행 중인 수주 건에 대한 실시간 공정 및 납기 현황입니다.
          </p>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <button
            style={{
              padding: "10px 15px",
              borderRadius: "8px",
              border: "1px solid var(--border-color)",
              background: "var(--bg-card)",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              fontWeight: 600,
            }}
          >
            <Icon.Calendar size={18} /> 납기 캘린더
          </button>
        </div>
      </header>

      <div className={styles.orderGrid}>
        {DUMMY_SO.map((so) => (
          <div key={so.id} className={styles.orderCard}>
            <div className={styles.cardHeader}>
              <span className={styles.soNumber}>{so.id}</span>
              <span
                style={{
                  fontSize: "0.8rem",
                  fontWeight: 700,
                  color: "var(--accent-color)",
                }}
              >
                {so.status}
              </span>
            </div>

            <h3 className={styles.clientName}>{so.client}</h3>
            <p
              style={{
                fontSize: "0.9rem",
                color: "var(--text-sub)",
                marginBottom: "1.5rem",
              }}
            >
              {so.title}
            </p>

            <div className={styles.progressArea}>
              <div className={styles.progressLabel}>
                <span>진행률</span>
                <span>{so.progress}%</span>
              </div>
              <div className={styles.progressBar}>
                <div
                  className={styles.progressFill}
                  style={{ width: `${so.progress}%` }}
                />
              </div>
            </div>

            <div className={styles.infoRow}>
              <span className={styles.label}>수주일자</span>
              <span className={styles.value}>{so.orderDate}</span>
            </div>
            <div className={styles.infoRow}>
              <span className={styles.label}>납기예정일</span>
              <span
                className={`${styles.value} ${new Date(so.dueDate) < new Date() ? styles.redText : ""}`}
              >
                {so.dueDate}
              </span>
            </div>
            <div className={styles.infoRow}>
              <span className={styles.label}>결제조건</span>
              <span className={styles.value}>선금 30% / 잔금 70%</span>
            </div>

            <div className={styles.footerAmount}>
              ￦{so.amount.toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OrderSoPage;
