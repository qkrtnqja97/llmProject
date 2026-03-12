import React, { useState } from "react";
import * as Icon from "lucide-react";
import styles from "./ResourcePage.module.css";

interface Resource {
  id: string;
  name: string;
  category: "IT 장비" | "소프트웨어" | "공용 자산" | "시설물";
  status: "사용가능" | "사용중" | "수리중" | "만료예정";
  user: string;
  lastUpdate: string;
}

const ResourcesPage: React.FC = () => {
  // 하드코딩된 자산 데이터
  const [resources] = useState<Resource[]>([
    {
      id: "RES-2026-001",
      name: "MacBook Pro 16 (개발팀)",
      category: "IT 장비",
      status: "사용중",
      user: "김철수",
      lastUpdate: "2026-01-15",
    },
    {
      id: "RES-2026-042",
      name: "Adobe Creative Cloud",
      category: "소프트웨어",
      status: "만료예정",
      user: "디자인팀",
      lastUpdate: "2026-02-28",
    },
    {
      id: "RES-2025-102",
      name: "사내 서버실 랙 #3",
      category: "시설물",
      status: "사용중",
      user: "인프라팀",
      lastUpdate: "2026-03-01",
    },
    {
      id: "RES-2026-088",
      name: "법인 차량 (G80 - 12가 3456)",
      category: "공용 자산",
      status: "사용가능",
      user: "-",
      lastUpdate: "2026-03-02",
    },
    {
      id: "RES-2026-005",
      name: "Dell UltraSharp 32",
      category: "IT 장비",
      status: "수리중",
      user: "관리팀",
      lastUpdate: "2026-02-10",
    },
  ]);

  const getStatusStyle = (status: string) => {
    switch (status) {
      case "사용가능":
        return styles.statusAvailable;
      case "사용중":
        return styles.statusInUse;
      case "수리중":
        return styles.statusRepair;
      case "만료예정":
        return styles.statusExpire;
      default:
        return "";
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>전사 자산 관리</h1>
          <p className={styles.subtitle}>
            사내 IT 기기, 소프트웨어 라이선스 및 공용 자산 현황을 조회합니다.
          </p>
        </div>
        <button className={styles.addBtn}>
          <Icon.Plus size={18} />
          자산 등록
        </button>
      </header>

      {/* 요약 카드 섹션 */}
      <div className={styles.summaryGrid}>
        <div className={styles.summaryCard}>
          <div
            className={styles.summaryIcon}
            style={{ background: "rgba(59, 130, 246, 0.1)", color: "#3b82f6" }}
          >
            <Icon.Monitor size={20} />
          </div>
          <div className={styles.summaryInfo}>
            <span>IT 장비</span>
            <strong>242 개</strong>
          </div>
        </div>
        <div className={styles.summaryCard}>
          <div
            className={styles.summaryIcon}
            style={{ background: "rgba(16, 185, 129, 0.1)", color: "#10b981" }}
          >
            <Icon.Key size={20} />
          </div>
          <div className={styles.summaryInfo}>
            <span>라이선스</span>
            <strong>18 건</strong>
          </div>
        </div>
        <div className={styles.summaryCard}>
          <div
            className={styles.summaryIcon}
            style={{ background: "rgba(245, 158, 11, 0.1)", color: "#f59e0b" }}
          >
            <Icon.Wrench size={20} />
          </div>
          <div className={styles.summaryInfo}>
            <span>수리/점검중</span>
            <strong>3 건</strong>
          </div>
        </div>
      </div>

      {/* 자산 목록 테이블 */}
      <div className={styles.tableCard}>
        <div className={styles.tableHeader}>
          <div className={styles.searchBar}>
            <Icon.Search size={16} />
            <input type="text" placeholder="자산명, 자산번호, 사용자 검색..." />
          </div>
          <div className={styles.filterGroup}>
            <Icon.Filter size={16} />
            <span>필터</span>
          </div>
        </div>

        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th className={styles.thId}>자산 번호</th>
                <th className={styles.thCategory}>카테고리</th>
                <th className={styles.thName}>자산명</th>
                <th className={styles.thStatus}>상태</th>
                <th className={styles.thUser}>실사용자</th>
                <th className={styles.thDate}>최종 업데이트</th>
                <th className={styles.thAction}>관리</th>
              </tr>
            </thead>
            <tbody>
              {resources.map((item) => (
                <tr key={item.id}>
                  <td className={styles.idText}>{item.id}</td>
                  <td className={styles.categoryText}>{item.category}</td>
                  <td className={`${styles.bold} ${styles.nameCell}`}>
                    <span title={item.name}>{item.name}</span>
                  </td>
                  <td>
                    <span
                      className={`${styles.statusBadge} ${getStatusStyle(item.status)}`}
                    >
                      {item.status}
                    </span>
                  </td>
                  <td className={styles.userText}>{item.user}</td>
                  <td className={styles.dateText}>{item.lastUpdate}</td>
                  <td>
                    <button className={styles.iconBtn}>
                      <Icon.MoreVertical size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ResourcesPage;
