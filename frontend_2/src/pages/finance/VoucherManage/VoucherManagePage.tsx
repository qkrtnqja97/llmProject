import * as Icon from "lucide-react";
import styles from "./VoucherManagePage.module.css";

const DUMMY_VOUCHERS = [
  {
    id: "V-2026-0001",
    date: "2026-03-03",
    account: "원재료매입",
    desc: "생산라인 부품 매입",
    amount: 15200000,
    type: "지출",
    status: "approved",
  },
  {
    id: "V-2026-0002",
    date: "2026-03-03",
    account: "여비교통비",
    desc: "영업팀 외근 주유비",
    amount: 45000,
    type: "지출",
    status: "pending",
  },
  {
    id: "V-2026-0003",
    date: "2026-03-02",
    account: "매출채권",
    desc: "A사 제품 납품 대금",
    amount: 42000000,
    type: "수입",
    status: "approved",
  },
  {
    id: "V-2026-0004",
    date: "2026-03-01",
    account: "복리후생비",
    desc: "사내 식당 식자재",
    amount: 2800000,
    type: "지출",
    status: "rejected",
  },
];

const VoucherManagePage = () => {
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.titleGroup}>
          <h1>일반 전표 관리</h1>
        </div>
        <button className={styles.addBtn}>
          <Icon.FilePlus2 size={18} /> 전표 작성
        </button>
      </header>

      <div className={styles.financeStats}>
        <div className={styles.statCard}>
          <span className={styles.statLabel}>오늘의 총 지출</span>
          <span className={styles.statValue}>18,045,000</span>
        </div>
        <div className={styles.statCard} style={{ borderColor: "#10b981" }}>
          <span className={styles.statLabel}>오늘의 총 수입</span>
          <span className={styles.statValue}>42,000,000</span>
        </div>
        <div className={styles.statCard} style={{ borderColor: "#f59e0b" }}>
          <span className={styles.statLabel}>결재 대기</span>
          <span className={styles.statValue}>5 건</span>
        </div>
        <div className={styles.statCard} style={{ borderColor: "#6366f1" }}>
          <span className={styles.statLabel}>미확정 전표</span>
          <span className={styles.statValue}>12 건</span>
        </div>
      </div>

      <div className={styles.tableCard}>
        <table className={styles.voucherTable}>
          <thead>
            <tr>
              <th>전표번호</th>
              <th>일자</th>
              <th>계정 과목</th>
              <th>적요</th>
              <th className={styles.amount}>금액</th>
              <th>구분</th>
              <th>상태</th>
            </tr>
          </thead>
          <tbody>
            {DUMMY_VOUCHERS.map((v) => (
              <tr key={v.id}>
                <td
                  style={{ fontFamily: "JetBrains Mono", fontSize: "0.8rem" }}
                >
                  {v.id}
                </td>
                <td>{v.date}</td>
                <td style={{ fontWeight: 700 }}>{v.account}</td>
                <td style={{ color: "var(--text-sub)" }}>{v.desc}</td>
                <td className={styles.amount}>￦{v.amount.toLocaleString()}</td>
                <td>{v.type}</td>
                <td>
                  <span className={`${styles.statusBadge} ${styles[v.status]}`}>
                    {v.status === "approved"
                      ? "승인"
                      : v.status === "pending"
                        ? "대기"
                        : "반려"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default VoucherManagePage;
