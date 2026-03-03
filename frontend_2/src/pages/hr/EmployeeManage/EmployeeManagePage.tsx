import * as Icon from "lucide-react";
import styles from "./EmployeeManagePage.module.css";

const DUMMY_EMPLOYEES = [
  {
    id: "2024-001",
    name: "김철수",
    rank: "팀장",
    dept: "생산관리팀",
    email: "cs.kim@factory.com",
    phone: "010-1234-5678",
    joinDate: "2024-01-15",
    status: "active",
  },
  {
    id: "2024-042",
    name: "이영희",
    rank: "과장",
    dept: "인사행정팀",
    email: "yh.lee@factory.com",
    phone: "010-2345-6789",
    joinDate: "2024-05-20",
    status: "active",
  },
  {
    id: "2025-012",
    name: "박상준",
    rank: "대리",
    dept: "구매물류팀",
    email: "sj.park@factory.com",
    phone: "010-3456-7890",
    joinDate: "2025-02-01",
    status: "active",
  },
  {
    id: "2025-088",
    name: "최윤지",
    rank: "사원",
    dept: "품질보증팀",
    email: "yj.choi@factory.com",
    phone: "010-4567-8901",
    joinDate: "2025-08-12",
    status: "on_leave",
  },
];

const EmployeeManagePage = () => {
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.titleGroup}>
          <h1>사원 정보 관리</h1>
          <p className={styles.subtitle}>
            인사 DB에 등록된 총 124명의 사원 정보를 관리합니다.
          </p>
        </div>
        <button className={styles.addBtn}>
          <Icon.UserPlus size={18} /> 신규 사원 등록
        </button>
      </header>

      {/* 실무형 요약 통계 바 */}
      <div className={styles.summaryRow}>
        <div className={styles.summaryCard}>
          <div className={styles.iconBox}>
            <Icon.Users size={20} />
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>전체 임직원</span>
            <span className={styles.statValue}>124</span>
          </div>
        </div>
        <div className={styles.summaryCard}>
          <div className={styles.iconBox} style={{ color: "#10b981" }}>
            <Icon.UserCheck size={20} />
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>정상 재직</span>
            <span className={styles.statValue}>118</span>
          </div>
        </div>
        <div className={styles.summaryCard}>
          <div className={styles.iconBox} style={{ color: "#f59e0b" }}>
            <Icon.UserMinus size={20} />
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>휴직/파견</span>
            <span className={styles.statValue}>6</span>
          </div>
        </div>
        <div className={styles.summaryCard}>
          <div className={styles.iconBox} style={{ color: "#6366f1" }}>
            <Icon.TrendingUp size={20} />
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>당월 입사</span>
            <span className={styles.statValue}>2</span>
          </div>
        </div>
      </div>

      {/* 필터 섹션 */}
      <div className={styles.actionRow}>
        <div className={styles.searchWrapper}>
          <Icon.Search size={18} />
          <input
            type="text"
            placeholder="사원명, 부서, 직급 또는 사번을 입력하세요..."
          />
        </div>
        <div className={styles.filterGroup}>
          <select className={styles.pageSizeSelect}>
            <option>전체 부서</option>
            <option>생산관리팀</option>
            <option>인사행정팀</option>
          </select>
        </div>
      </div>

      {/* 사원 카드 그리드 */}
      <div className={styles.employeeGrid}>
        {DUMMY_EMPLOYEES.map((emp) => (
          <div key={emp.id} className={styles.employeeCard}>
            {emp.status === "active" && <div className={styles.activeBar} />}
            <div className={styles.cardTop}>
              <div className={styles.avatar}>{emp.name.charAt(0)}</div>
              <div className={styles.empBasic}>
                <span className={styles.empName}>{emp.name}</span>
                <span className={styles.empRank}>
                  {emp.dept} · {emp.rank}
                </span>
              </div>
            </div>
            <div className={styles.cardContent}>
              <div className={styles.infoItem}>
                <span className={styles.label}>사번</span>
                <span className={styles.value}>{emp.id}</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.label}>이메일</span>
                <span className={styles.value}>{emp.email}</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.label}>연락처</span>
                <span className={styles.value}>{emp.phone}</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.label}>입사일자</span>
                <span className={styles.value}>{emp.joinDate}</span>
              </div>
            </div>
            <div className={styles.cardFooter}>
              <button className={styles.detailBtn}>상세 프로필 보기</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EmployeeManagePage;
