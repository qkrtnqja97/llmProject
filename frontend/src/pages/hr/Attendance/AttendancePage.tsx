import * as Icon from "lucide-react";
import styles from "./AttendancePage.module.css";

const DUMMY_ATTENDANCE = [
  {
    id: 1,
    name: "김철수",
    dept: "생산관리팀",
    date: "2026-03-03",
    checkIn: "08:52",
    checkOut: "18:10",
    status: "normal",
    note: "정상 근무",
  },
  {
    id: 2,
    name: "이영희",
    dept: "인사행정팀",
    date: "2026-03-03",
    checkIn: "09:15",
    checkOut: "18:05",
    status: "late",
    note: "지하철 연착",
  },
  {
    id: 3,
    name: "박상준",
    dept: "구매물류팀",
    date: "2026-03-03",
    checkIn: "08:45",
    checkOut: "-",
    status: "working",
    note: "-",
  },
  {
    id: 4,
    name: "최윤지",
    dept: "품질보증팀",
    date: "2026-03-03",
    checkIn: "-",
    checkOut: "-",
    status: "vacation",
    note: "연차",
  },
];

const AttendancePage = () => {
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.titleWithDate}>
          <h1>전사 근태 기록</h1>
          <span className={styles.currentDate}>2026.03.03 (TUE)</span>
        </div>
        <div className={styles.btnGroup}>
          <button className={styles.secondaryBtn}>
            <Icon.Download size={16} /> 리포트 추출
          </button>
          <button className={styles.addBtn}>
            <Icon.Plus size={16} /> 근태 수동 입력
          </button>
        </div>
      </header>

      {/* 근태 요약 섹션 */}
      <div className={styles.attendanceStats}>
        <div className={styles.statItem}>
          <div className={styles.statText}>
            <span className={styles.label}>출근 인원</span>
            <span className={styles.count}>112 / 124</span>
          </div>
          <Icon.CheckCircle2 color="#10b981" size={24} />
        </div>
        <div className={styles.statItem}>
          <div className={styles.statText}>
            <span className={styles.label}>지각자</span>
            <span className={styles.count} style={{ color: "#f59e0b" }}>
              3
            </span>
          </div>
          <Icon.AlertCircle color="#f59e0b" size={24} />
        </div>
        <div className={styles.statItem}>
          <div className={styles.statText}>
            <span className={styles.label}>연차/휴가</span>
            <span className={styles.count} style={{ color: "#6366f1" }}>
              8
            </span>
          </div>
          <Icon.Palmtree color="#6366f1" size={24} />
        </div>
      </div>

      {/* 실무형 데이터 테이블 */}
      <div className={styles.tableCard}>
        <div className={styles.tableContainer}>
          <table className={styles.attendanceTable}>
            <thead>
              <tr>
                <th>사원정보</th>
                <th>일자</th>
                <th>출근시간</th>
                <th>퇴근시간</th>
                <th>근무상태</th>
                <th>비고</th>
                <th>관리</th>
              </tr>
            </thead>
            <tbody>
              {DUMMY_ATTENDANCE.map((atd) => (
                <tr key={atd.id}>
                  <td>
                    <div style={{ fontWeight: 700, color: "var(--text-main)" }}>
                      {atd.name}
                    </div>
                    <div
                      style={{ fontSize: "0.75rem", color: "var(--text-sub)" }}
                    >
                      {atd.dept}
                    </div>
                  </td>
                  <td className={styles.timeCell}>{atd.date}</td>
                  <td
                    className={`${styles.timeCell} ${atd.status === "late" ? styles.redText : ""}`}
                  >
                    {atd.checkIn}
                  </td>
                  <td className={styles.timeCell}>{atd.checkOut}</td>
                  <td>
                    {/* TSX의 styles[atd.status] 매핑이 CSS 클래스와 일치하도록 수정됨 */}
                    <span
                      className={`${styles.statusBadge} ${styles[atd.status]}`}
                    >
                      <span className={styles.statusDot} />
                      {atd.status === "normal" && "정상출근"}
                      {atd.status === "late" && "지각"}
                      {atd.status === "working" && "근무중"}
                      {atd.status === "vacation" && "연차"}
                    </span>
                  </td>
                  <td style={{ fontSize: "0.85rem", color: "var(--text-sub)" }}>
                    {atd.note}
                  </td>
                  <td>
                    <div className={styles.btnGroup}>
                      <button className={styles.iconBtn} title="수정">
                        <Icon.Edit3 size={14} />
                      </button>
                      <button className={styles.iconBtn} title="로그 확인">
                        <Icon.History size={14} />
                      </button>
                    </div>
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

export default AttendancePage;
