import { useState } from "react";
import * as Icon from "lucide-react";
import styles from "./OrderManagePage.module.css";

// 📍 하드코딩된 더미 데이터
const DUMMY_ORDERS = [
  {
    id: "PO-2026-001",
    supplier: "한성 테크놀로지",
    title: "메인보드 외 3건",
    date: "2026-03-01",
    deliveryDate: "2026-03-10",
    status: "pending", // 발주대기
    amount: 15400000,
    manager: "김철수 팀장",
  },
  {
    id: "PO-2026-002",
    supplier: "글로벌 로지스틱스",
    title: "산업용 센서 모듈",
    date: "2026-02-28",
    deliveryDate: "2026-03-05",
    status: "ordered", // 발주완료
    amount: 8200000,
    manager: "이영희 과장",
  },
  {
    id: "PO-2026-003",
    supplier: "미래 금속공업",
    title: "알루미늄 프레임 세트",
    date: "2026-02-20",
    deliveryDate: "2026-02-25",
    status: "received", // 입고완료
    amount: 3500000,
    manager: "박상준 대리",
  },
  {
    id: "PO-2026-004",
    supplier: "세종 정밀",
    title: "베어링 및 기어류",
    date: "2026-03-02",
    deliveryDate: "2026-03-15",
    status: "pending",
    amount: 4200000,
    manager: "김철수 팀장",
  },
];

const OrderManagePage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  // 상태 텍스트 헬퍼
  const getStatusInfo = (status: string) => {
    switch (status) {
      case "pending":
        return { text: "발주대기", class: styles.pending };
      case "ordered":
        return { text: "발주완료", class: styles.ordered };
      case "received":
        return { text: "입고완료", class: styles.received };
      default:
        return { text: "알수없음", class: "" };
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.titleSection}>
          <Icon.ShoppingCart size={28} className={styles.titleIcon} />
          <h1>발주 및 입고 관리</h1>
        </div>
        <button className={styles.addBtn}>
          <Icon.FilePlus size={18} /> 신규 발주서 작성
        </button>
      </header>

      {/* 컨트롤 섹션 */}
      <div className={styles.tableControls}>
        <div className={styles.searchBar}>
          <Icon.Search size={18} />
          <input
            type="text"
            placeholder="발주 번호 또는 공급처 검색..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className={styles.filterGroup}>
          <select
            className={styles.selectBox}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">전체 상태</option>
            <option value="pending">발주대기</option>
            <option value="ordered">발주완료</option>
            <option value="received">입고완료</option>
          </select>

          <select className={styles.selectBox}>
            <option>최근 30일</option>
            <option>지난 달</option>
            <option>2026년 전체</option>
          </select>
        </div>
      </div>

      {/* 발주 카드 리스트 */}
      <div className={styles.orderGrid}>
        {DUMMY_ORDERS.map((order) => {
          const status = getStatusInfo(order.status);
          return (
            <div key={order.id} className={styles.orderCard}>
              <div className={styles.cardHeader}>
                <span className={styles.orderId}>{order.id}</span>
                <span className={`${styles.statusBadge} ${status.class}`}>
                  {status.text}
                </span>
              </div>

              <h3 className={styles.orderTitle}>{order.title}</h3>

              <div className={styles.orderDetailRow}>
                <span className={styles.label}>공급처</span>
                <span className={styles.value}>{order.supplier}</span>
              </div>
              <div className={styles.orderDetailRow}>
                <span className={styles.label}>발주일자</span>
                <span className={styles.value}>{order.date}</span>
              </div>
              <div className={styles.orderDetailRow}>
                <span className={styles.label}>입고예정</span>
                <span className={styles.value}>{order.deliveryDate}</span>
              </div>
              <div className={styles.orderDetailRow}>
                <span className={styles.label}>담당자</span>
                <span className={styles.value}>{order.manager}</span>
              </div>

              <div className={styles.totalAmount}>
                ￦{order.amount.toLocaleString()}
              </div>
            </div>
          );
        })}
      </div>

      {/* 페이지네이션 (하드코딩) */}
      <div className={styles.pagination}>
        <button disabled>
          <Icon.ChevronLeft size={20} />
        </button>
        <button className={styles.activePage}>1</button>
        <button>
          <Icon.ChevronRight size={20} />
        </button>
      </div>
    </div>
  );
};

export default OrderManagePage;
