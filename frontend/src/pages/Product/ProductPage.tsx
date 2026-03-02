import React from "react";
import styles from "./ProductPage.module.css";
import common from "../../app/styles/Global.module.css";

const ProductPage: React.FC = () => {
  return (
    <div className={common.pageSectionCard}>
      <h3 className={common.pageTitle}>🛠️ 제품 관리</h3>
      <p className={common.pageText}>
        판매 및 유통되는 제품의 상세 정보입니다.
      </p>

      <div className={styles.grid}>
        {[1, 2].map((i) => (
          <div key={i} className={styles.productCard}>
            <div className={styles.imagePlaceholder}>🖼️</div>
            <div className={styles.content}>
              <span className={styles.category}>Electronics</span>
              <p className={styles.name}>스마트 센서 모듈 V{i}</p>
              <p className={styles.price}>₩ 89,000</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductPage;
