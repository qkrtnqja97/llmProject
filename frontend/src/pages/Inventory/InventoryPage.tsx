import React from "react";
import styles from "./InventoryPage.module.css";
import common from "../../app/styles/Global.module.css";

const InventoryPage: React.FC = () => {
  return (
    <div className={common.pageSectionCard}>
      <h3 className={common.pageTitle}>📦 재고 관리</h3>
      <p className={common.pageText}>현재 창고 내 품목 및 수량을 확인합니다.</p>

      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.th}>품목명</th>
              <th className={styles.th}>현재고</th>
              <th className={styles.th}>상태</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className={styles.td}>A급 반도체 소자</td>
              <td className={styles.td}>1,250 EA</td>
              <td className={styles.td}>
                <span className={styles.statusBadge}>안전</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default InventoryPage;
