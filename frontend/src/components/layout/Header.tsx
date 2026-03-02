import React from "react";
import { useLocation } from "react-router-dom";
import styles from "./Header.module.css";

// 타이틀 상수는 외부로 분리하여 관리 (나중에 별도 config 파일로 옮겨도 좋음)
const PAGE_TITLES: Record<string, string> = {
  "/": "홈",
  "/ai": "AI 어시스턴트",
  "/dashboard": "운영 대시보드",
  "/archive": "문서 자료실",
  "/insights": "비즈니스 인사이트",
  "/company": "회사 설정",
  "/tasks": "업무 작성",
  "/inventory": "재고 현황",
  "/orders": "발주 관리",
  "/products": "제품 리스트",
  "/contacts": "연락처 주소록",
  "/history": "검색 히스토리",
};

const Header: React.FC = () => {
  const location = useLocation();

  // 경로가 정확히 일치하지 않는 경우(예: /products/1)를 대비한 로직 처리
  const currentTitle = PAGE_TITLES[location.pathname] || "Console";

  return (
    <header className={styles.header}>
      <h2 className={styles.title}>{currentTitle}</h2>

      {/* 우측 영역: 알림, 헬프 데스크 등 확장 가능 */}
      <div className={styles.rightSection}>
        {/* 필요한 경우 여기에 컴포넌트 추가 */}
      </div>
    </header>
  );
};

export default Header;
