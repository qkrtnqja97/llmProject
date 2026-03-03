import React, { useState } from "react";
import * as Icon from "lucide-react";
import styles from "./WorkLogPage.module.css";

interface LogEntry {
  id: number;
  date: string;
  category: string;
  title: string;
  content: string;
  status: "완료" | "진행중" | "대기";
}

const CATEGORIES = ["재고실사", "입고검수", "출고지시", "영업상담", "기타"];

const WorkLogPage: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      id: 1,
      date: "2026-03-02",
      category: "재고실사",
      title: "A구역 반도체 부품 수량 점검",
      content: "IC 칩셋 2종 수량 오차 확인 후 조정 완료.",
      status: "완료",
    },
    {
      id: 2,
      date: "2026-03-03",
      category: "입고검수",
      title: "신규 발주분(GPU) 검수 진행",
      content: "외관 파손 여부 확인 중이며 오후 내 완료 예정.",
      status: "진행중",
    },
  ]);

  const [newLog, setNewLog] = useState({
    category: "재고실사",
    title: "",
    content: "",
  });

  const handleAddLog = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newLog.title.trim()) return;

    const entry: LogEntry = {
      id: Date.now(),
      date: new Date().toISOString().split("T")[0],
      category: newLog.category,
      title: newLog.title,
      content: newLog.content,
      status: "완료",
    };

    setLogs([entry, ...logs]);
    setNewLog({ category: "재고실사", title: "", content: "" });
  };

  const deleteLog = (id: number) => {
    setLogs(logs.filter((log) => log.id !== id));
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>업무 일지 작성</h1>
        <p className={styles.subtitle}>
          오늘의 주요 업무 내용을 기록하고 관리합니다.
        </p>
      </header>

      <div className={styles.contentGrid}>
        {/* 왼쪽: 작성 폼 */}
        <section className={styles.formCard}>
          <div className={styles.cardHeader}>
            <Icon.PenLine size={18} className={styles.accentIcon} />
            <h2>새 일지 기록</h2>
          </div>
          <form onSubmit={handleAddLog} className={styles.form}>
            <div className={styles.formGroup}>
              <label>업무 분류</label>
              <select
                value={newLog.category}
                onChange={(e) =>
                  setNewLog({ ...newLog, category: e.target.value })
                }
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.formGroup}>
              <label>제목</label>
              <input
                type="text"
                placeholder="핵심 업무 내용을 입력하세요"
                value={newLog.title}
                onChange={(e) =>
                  setNewLog({ ...newLog, title: e.target.value })
                }
              />
            </div>
            <div className={styles.formGroup}>
              <label>세부 내용</label>
              <textarea
                rows={5}
                placeholder="상세 내역을 기록하세요"
                value={newLog.content}
                onChange={(e) =>
                  setNewLog({ ...newLog, content: e.target.value })
                }
              />
            </div>
            <button type="submit" className={styles.submitBtn}>
              <Icon.Save size={16} />
              저장하기
            </button>
          </form>
        </section>

        {/* 오른쪽: 목록 */}
        <section className={styles.listCard}>
          <div className={styles.cardHeader}>
            <Icon.History size={18} className={styles.accentIcon} />
            <h2>최근 기록 ({logs.length})</h2>
          </div>
          <div className={styles.logList}>
            {logs.map((log) => (
              <div key={log.id} className={styles.logItem}>
                <div className={styles.logMeta}>
                  <span className={styles.logDate}>{log.date}</span>
                  <span className={styles.logCategory}>{log.category}</span>
                  <button
                    onClick={() => deleteLog(log.id)}
                    className={styles.deleteBtn}
                  >
                    <Icon.Trash2 size={14} />
                  </button>
                </div>
                <h3 className={styles.logTitle}>{log.title}</h3>
                <p className={styles.logContent}>{log.content}</p>
                <div className={styles.logStatus}>
                  <span
                    className={`${styles.statusBadge} ${log.status === "완료" ? styles.done : styles.doing}`}
                  >
                    {log.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

export default WorkLogPage;
