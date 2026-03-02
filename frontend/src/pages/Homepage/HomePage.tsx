import React from "react";
import styles from "./HomePage.module.css";

const HomePage: React.FC = () => {
  return (
    <div className={styles.heroSection}>
      <h1 className={styles.mainTitle}>Biz AI Console</h1>
      <p className={styles.description}>왼쪽 메뉴를 선택하여 시작하세요.</p>
    </div>
  );
};

export default HomePage;
