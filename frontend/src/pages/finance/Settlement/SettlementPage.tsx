import * as Icon from "lucide-react";
import styles from "./SettlementPage.module.css";

const SettlementPage = () => {
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1
            style={{
              fontSize: "1.8rem",
              fontWeight: 800,
              color: "var(--text-main)",
            }}
          >
            2026년 02월 결산 리포트
          </h1>
          <p className={styles.label}>최종 업데이트: 2026-03-03 09:00:01</p>
        </div>
        <div style={{ display: "flex", gap: "10px" }}>
          <button className={styles.secondaryBtn}>
            <Icon.Printer size={18} /> 출력
          </button>
          <button className={styles.addBtn}>
            <Icon.CheckSquare size={18} /> 결산 확정
          </button>
        </div>
      </header>

      <div className={styles.summaryBox}>
        <div className={styles.summaryItem}>
          <span className={styles.label}>총 매출액</span>
          <span className={styles.val}>428,500,000</span>
        </div>
        <div className={styles.summaryItem}>
          <span className={styles.label}>총 비용</span>
          <span className={`${styles.val} ${styles.negative}`}>
            -312,400,000
          </span>
        </div>
        <div className={styles.summaryItem}>
          <span className={styles.label}>당기순이익</span>
          <span className={`${styles.val} ${styles.positive}`}>
            116,100,000
          </span>
        </div>
      </div>

      <div className={styles.reportGrid}>
        <div className={styles.mainCard}>
          <h3 className={styles.cardTitle}>
            <Icon.FileText size={20} className={styles.accentIcon} /> 손익계산서
            요약
          </h3>
          <table className={styles.settlementTable}>
            <tbody>
              <tr style={{ fontWeight: 700 }}>
                <td>Ⅰ. 매출액</td>
                <td align="right">428,500,000</td>
              </tr>
              <tr>
                <td className={styles.indent}>제품매출</td>
                <td align="right">380,000,000</td>
              </tr>
              <tr>
                <td className={styles.indent}>서비스매출</td>
                <td align="right">48,500,000</td>
              </tr>
              <tr style={{ fontWeight: 700 }}>
                <td>Ⅱ. 매출원가</td>
                <td align="right">(250,000,000)</td>
              </tr>
              <tr className={styles.totalRow}>
                <td>Ⅲ. 매출총이익</td>
                <td align="right">178,500,000</td>
              </tr>
              <tr>
                <td>Ⅳ. 판매비와관리비</td>
                <td align="right">(62,400,000)</td>
              </tr>
              <tr>
                <td className={styles.indent}>급여</td>
                <td align="right">45,000,000</td>
              </tr>
              <tr>
                <td className={styles.indent}>복리후생비</td>
                <td align="right">17,400,000</td>
              </tr>
              <tr
                className={styles.totalRow}
                style={{ color: "var(--accent-color)" }}
              >
                <td>Ⅴ. 영업이익</td>
                <td align="right">116,100,000</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className={styles.mainCard}>
          <h3 className={styles.cardTitle}>
            <Icon.PieChart size={20} className={styles.accentIcon} /> 지출 비중
          </h3>
          <div
            style={{
              height: "250px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              border: "1px dashed var(--border-color)",
              borderRadius: "12px",
              background: "var(--bg-item)",
            }}
          >
            <p className={styles.label}>Chart Placeholder</p>
          </div>
          <div style={{ marginTop: "20px" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: "8px",
                fontSize: "0.9rem",
                color: "var(--text-main)",
                fontWeight: 600,
              }}
            >
              <span>원재료비</span>
              <span>65%</span>
            </div>
            <div className={styles.progressRail}>
              <div
                style={{
                  width: "65%",
                  height: "100%",
                  background: "var(--accent-color)",
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettlementPage;
