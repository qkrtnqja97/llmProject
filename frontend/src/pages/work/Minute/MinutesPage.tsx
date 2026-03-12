import React, { useState } from "react";
import * as Icon from "lucide-react";
import styles from "./MinutesPage.module.css";

interface MeetingMinute {
  id: string;
  date: string;
  title: string;
  organizer: string;
  attendees: string[];
  agendas: string[];
  decisions: string[];
  actionItems: { task: string; owner: string; dueDate: string }[];
}

const MinutesPage: React.FC = () => {
  const [minutes] = useState<MeetingMinute[]>([
    {
      id: "MOM-2026-0302",
      date: "2026-03-02",
      title: "1분기 재고 실사 일정 및 인력 배치 논의",
      organizer: "박진수 팀장",
      attendees: ["김철수", "이영희", "최민호"],
      agendas: [
        "A구역 반도체 부품 전수 조사 계획 수립",
        "임시 아르바이트 인력 안전 교육 및 배치",
      ],
      decisions: [
        "실사는 3월 15일부터 18일까지 총 4일간 진행하기로 결정함.",
        "A구역 우선 진행 후 데이터 검증을 거쳐 B구역으로 이동함.",
      ],
      actionItems: [
        {
          task: "전사 재고 리스트 최신화 및 실사표 출력",
          owner: "이영희",
          dueDate: "2026-03-10",
        },
        {
          task: "현장 투입 인력 대상 안전 교육 자료 준비",
          owner: "최민호",
          dueDate: "2026-03-12",
        },
      ],
    },
    {
      id: "MOM-2026-0225",
      date: "2026-02-25",
      title: "공급망 리스크 관리 및 신규 협력사 평가 결과 공유회",
      organizer: "이현우 본부장",
      attendees: ["박진수", "정다은", "강현구", "신예지"],
      agendas: ["물류 단가 상승에 따른 대응책", "동남아 신규 공급 라인 확보"],
      decisions: [
        "기존 운송 계약 6개월 연장 협의",
        "베트남 신규 업체 후보군 실사 진행",
      ],
      actionItems: [
        {
          task: "물류 계약 연장 관련 공문 발송",
          owner: "정다은",
          dueDate: "2026-03-05",
        },
      ],
    },
  ]);

  const [selectedId, setSelectedId] = useState<string | null>(minutes[0].id);
  const selectedMinute = minutes.find((m) => m.id === selectedId);

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>회의록 관리</h1>
          <p className={styles.subtitle}>
            사내 주요 회의 내용 및 결정 사항을 체계적으로 관리합니다.
          </p>
        </div>
        <button className={styles.createBtn}>
          <Icon.FilePlus size={18} /> 새 회의록 작성
        </button>
      </header>

      <div className={styles.mainContent}>
        {/* 왼쪽 사이드바: 회의 목록 */}
        <aside className={styles.sidebar}>
          <div className={styles.searchBox}>
            <Icon.Search size={16} />
            <input type="text" placeholder="회의명 검색..." />
          </div>
          <div className={styles.minuteList}>
            {minutes.map((m) => (
              <div
                key={m.id}
                className={`${styles.minuteItem} ${
                  selectedId === m.id ? styles.active : ""
                }`}
                onClick={() => setSelectedId(m.id)}
              >
                <span className={styles.mDate}>{m.date}</span>
                <span className={styles.mTitle}>{m.title}</span>
              </div>
            ))}
          </div>
        </aside>

        {/* 오른쪽 뷰어: 상세 내용 */}
        <main className={styles.viewer}>
          {selectedMinute ? (
            <div className={styles.minuteDetail}>
              <div className={styles.viewerHeader}>
                <span className={styles.mId}>{selectedMinute.id}</span>
                <h2 className={styles.viewerTitle}>{selectedMinute.title}</h2>
                <div className={styles.metaRow}>
                  <div className={styles.metaItem}>
                    <Icon.Calendar size={14} />{" "}
                    <span>{selectedMinute.date}</span>
                  </div>
                  <div className={styles.metaItem}>
                    <Icon.User size={14} />{" "}
                    <span>주관: {selectedMinute.organizer}</span>
                  </div>
                  <div className={styles.metaItem}>
                    <Icon.Users size={14} />{" "}
                    <span>참석: {selectedMinute.attendees.join(", ")}</span>
                  </div>
                </div>
              </div>

              <div className={styles.contentBody}>
                <section className={styles.section}>
                  <h3>
                    <Icon.ListChecks size={18} /> 주요 안건
                  </h3>
                  <div className={styles.agendaGrid}>
                    {selectedMinute.agendas.map((a, i) => (
                      <div key={i} className={styles.agendaCard}>
                        {a}
                      </div>
                    ))}
                  </div>
                </section>

                <section className={styles.section}>
                  <h3>
                    <Icon.CheckCircle2 size={18} /> 결정 사항
                  </h3>
                  <div className={styles.decisionBox}>
                    {selectedMinute.decisions.map((d, i) => (
                      <div key={i} className={styles.decisionItem}>
                        <span className={styles.bullet}>•</span>
                        <p>{d}</p>
                      </div>
                    ))}
                  </div>
                </section>

                <section className={styles.section}>
                  <h3>
                    <Icon.ArrowRightCircle size={18} /> 후속 작업 (Action Items)
                  </h3>
                  <div className={styles.tableWrapper}>
                    <table className={styles.actionTable}>
                      <thead>
                        <tr>
                          <th className={styles.thTask}>할 일</th>
                          <th className={styles.thOwner}>담당자</th>
                          <th className={styles.thDate}>기한</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedMinute.actionItems.map((item, i) => (
                          <tr key={i}>
                            <td className={styles.taskCell}>{item.task}</td>
                            <td className={styles.ownerCell}>{item.owner}</td>
                            <td className={styles.dateCell}>{item.dueDate}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </section>
              </div>
            </div>
          ) : (
            <div className={styles.empty}>
              <Icon.Inbox size={48} />
              <p>회의록을 선택해 주세요.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default MinutesPage;
