import React from "react";
import styles from "./OrderPage.module.css";
import common from "../../app/styles/Global.module.css";

const OrderPage: React.FC = () => {
  return (
    <div className={common.pageSectionCard}>
      <h3 className={common.pageTitle}>🛒 발주 관리</h3>
      <p className={common.pageText}>
        진행 중인 발주 건과 과거 이력을 관리합니다.
      </p>

      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.th}>발주 번호</th>
              <th className={styles.th}>거래처</th>
              <th className={styles.th}>금액</th>
              <th className={styles.th}>상태</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className={styles.td}>ORD-2024-001</td>
              <td className={styles.td}>(주) 글로벌 테크</td>
              <td className={styles.td}>₩ 4,500,000</td>
              <td className={styles.td}>
                <span className={styles.statusPending}>대기 중</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default OrderPage;
