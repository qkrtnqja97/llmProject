import React, { useState, useEffect, useMemo } from "react";
import * as LucideIcons from "lucide-react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import { workService } from "../../services/workService";
import styles from "./TaskCreatePage.module.css";

interface Task {
  id: number;
  emp_id: string;
  title: string;
  content: string;
  priority: "high" | "medium" | "low";
  due_date: string | null;
  created_at: string;
}

const TaskCreatePage = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [priority, setPriority] = useState<"high" | "medium" | "low">("medium");
  const [dueDate, setDueDate] = useState("");
  const [isViewMode, setIsViewMode] = useState(false);

  // ESC 키로 모달 닫기
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isModalOpen) {
        resetFormAndClose();
      }
    };
    if (isModalOpen) window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isModalOpen]);

  // [수정] 데이터 로드 로직 방어 강화
  const fetchTasks = async () => {
    try {
      const response = await workService.getTasks();
      // 백엔드 응답이 { items: [] } 인지 그냥 [] 인지 관계없이 처리
      const data = response?.items || response;
      setTasks(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("데이터 로드 실패", error);
      setTasks([]); // 에러 시 빈 배열로 초기화하여 정렬 에러 방지
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  // [수정] 날짜 보정 함수 안정화 (Invalid Date 방지)
  const formatLocalDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return "";

    try {
      // 1. "2026-03-02" 형태면 그대로 반환
      if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr;

      // 2. ISO 형태일 경우 로컬 시간대 보정
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return "";

      const offset = date.getTimezoneOffset() * 60000;
      const localDate = new Date(date.getTime() - offset);
      return localDate.toISOString().split("T")[0];
    } catch (e) {
      return "";
    }
  };

  // [수정] 정렬 로직 방어 코드 (튕김 방지 핵심)
  const sortedTasks = useMemo(() => {
    if (!Array.isArray(tasks)) return [];

    return [...tasks].sort((a, b) => {
      const dateA = new Date(a.due_date || a.created_at || 0).getTime();
      const dateB = new Date(b.due_date || b.created_at || 0).getTime();

      const valA = isNaN(dateA) ? 0 : dateA;
      const valB = isNaN(dateB) ? 0 : dateB;

      return valA - valB;
    });
  }, [tasks]);

  const resetFormAndClose = () => {
    setEditingId(null);
    setTitle("");
    setContent("");
    setPriority("medium");
    setDueDate("");
    setIsViewMode(false);
    setIsModalOpen(false);
  };

  const handleDeleteTask = async (id: number) => {
    if (!window.confirm("정말로 이 업무를 삭제하시겠습니까?")) return;
    try {
      await workService.deleteTask(id);
      alert("삭제가 완료되었습니다.");
      await fetchTasks();
      resetFormAndClose();
    } catch (error: any) {
      const serverMessage = error.response?.data?.detail;
      alert(serverMessage || "삭제 중 오류가 발생했습니다.");
    }
  };

  const openViewModal = (task: Task) => {
    setEditingId(task.id);
    setTitle(task.title || "");
    setContent(task.content || "");
    setPriority(task.priority || "medium");
    setDueDate(formatLocalDate(task.due_date));
    setIsViewMode(true);
    setIsModalOpen(true);
  };

  const handleSaveTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isViewMode) return;

    try {
      const taskData = {
        title,
        content,
        priority,
        due_date: dueDate || null,
        status: "todo",
      };
      if (editingId) {
        await workService.updateTask(editingId, taskData);
        alert("업무가 수정되었습니다.");
      } else {
        await workService.createTask(taskData);
        alert("새 업무가 등록되었습니다.");
      }
      await fetchTasks();
      resetFormAndClose();
    } catch (error: any) {
      const serverMessage = error.response?.data?.detail;
      alert(serverMessage || "저장 중 오류가 발생했습니다.");
    }
  };

  // [수정] 캘린더 이벤트 생성 시 안전한 날짜 참조
  const calendarEvents = useMemo(() => {
    return tasks.map((task) => ({
      id: String(task.id),
      title: task.title,
      start: task.due_date || task.created_at,
      backgroundColor: "transparent",
      borderColor: "transparent",
      extendedProps: { ...task },
    }));
  }, [tasks]);

  const renderDayCellContent = (dayInfo: any) => (
    <span className="fc-daygrid-day-number">
      {dayInfo.dayNumberText.replace("일", "")}
    </span>
  );

  const renderEventContent = (eventInfo: any) => {
    const p = eventInfo.event.extendedProps.priority || "medium";
    return (
      <div className={styles.eventWrapper}>
        <span className={`${styles.eventDot} ${styles[p]}`}></span>
        <span className={styles.eventTitle}>{eventInfo.event.title}</span>
      </div>
    );
  };

  return (
    <div className={styles.mainContainer}>
      <div className={styles.contentWrapper}>
        <section
          className={`${styles.calendarCard} ${isMinimized ? styles.minimizedMode : ""}`}
        >
          <div className={styles.calendarHeaderRow}>
            <div className={styles.headerLeft}>
              <h2 className={styles.sectionTitle}>업무 캘린더</h2>
              <button
                className={styles.minimizeBtn}
                onClick={() => setIsMinimized(!isMinimized)}
              >
                {isMinimized ? (
                  <LucideIcons.Maximize2 size={18} />
                ) : (
                  <LucideIcons.Minimize2 size={18} />
                )}
              </button>
            </div>
            {!isMinimized && (
              <button
                className={styles.topAddBtn}
                onClick={() => {
                  resetFormAndClose();
                  setIsModalOpen(true);
                }}
              >
                <LucideIcons.Plus size={16} /> 새 업무 등록
              </button>
            )}
          </div>

          <div className={styles.calendarContainer}>
            <FullCalendar
              plugins={[dayGridPlugin, interactionPlugin]}
              initialView={isMinimized ? "dayGridWeek" : "dayGridMonth"}
              key={isMinimized ? "week" : "month"}
              events={calendarEvents}
              dayCellContent={renderDayCellContent}
              eventDidMount={(info) => {
                info.el.style.cursor = "pointer";
                info.el.ondblclick = (e) => {
                  e.stopPropagation();
                  openViewModal(info.event.extendedProps as Task);
                };
              }}
              eventContent={renderEventContent}
              headerToolbar={
                isMinimized
                  ? false
                  : { left: "prev,next today", center: "title", right: "" }
              }
              locale="ko"
              height={isMinimized ? 180 : 650}
              dayMaxEvents={true}
              selectable={true}
              moreLinkClick="popover"
            />
          </div>
        </section>

        {isMinimized && (
          <section className={styles.listSection}>
            <div className={styles.boardHeader}>
              <div className={styles.colTitle}>업무명</div>
              <div className={styles.colEmp}>사번</div>
              <div className={styles.colDate}>업무 일정</div>
              <div className={styles.colAction}>관리</div>
            </div>
            <div className={styles.scrollArea}>
              {sortedTasks.map((task) => (
                <div
                  key={task.id}
                  className={styles.boardRow}
                  onClick={() => openViewModal(task)}
                  style={{ cursor: "pointer" }}
                >
                  <div className={styles.colTitle}>
                    <span
                      className={`${styles.priorityDot} ${styles[task.priority]}`}
                    />
                    <span className={styles.titleText}>{task.title}</span>
                  </div>
                  <div className={styles.colEmp}>{task.emp_id}</div>
                  <div className={styles.colDate}>
                    {task.due_date
                      ? `🗓️ ${formatLocalDate(task.due_date)}`
                      : `✍️ ${formatLocalDate(task.created_at)}`}
                  </div>
                  <div
                    className={styles.colAction}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <button
                      className={styles.editBtn}
                      onClick={() => {
                        openViewModal(task);
                        setIsViewMode(false);
                      }}
                    >
                      <LucideIcons.Pencil size={14} />
                    </button>
                    <button
                      className={styles.deleteBtn}
                      onClick={() => handleDeleteTask(task.id)}
                    >
                      <LucideIcons.Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>

      {isModalOpen && (
        <div className={styles.modalOverlay} onClick={resetFormAndClose}>
          <div
            className={styles.modalContent}
            onClick={(e) => e.stopPropagation()}
          >
            <div className={styles.modalHeader}>
              <h3>
                {isViewMode
                  ? "업무 상세 정보"
                  : editingId
                    ? "업무 수정"
                    : "새 업무 등록"}
              </h3>
              <button
                type="button"
                className={styles.closeBtn}
                onClick={resetFormAndClose}
              >
                <LucideIcons.X size={20} />
              </button>
            </div>
            <form onSubmit={handleSaveTask}>
              <div className={styles.inputGroup}>
                <label>업무 일정 설정</label>
                <input
                  type="date"
                  className={styles.input}
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  readOnly={isViewMode}
                />
              </div>
              <div className={styles.inputGroup}>
                <label>우선순위</label>
                <select
                  className={styles.input}
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as any)}
                  disabled={isViewMode}
                >
                  <option value="high">긴급 (빨강)</option>
                  <option value="medium">보통 (파랑)</option>
                  <option value="low">낮음 (회색)</option>
                </select>
              </div>
              <div className={styles.inputGroup}>
                <label>제목</label>
                <input
                  className={styles.input}
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  readOnly={isViewMode}
                  required
                />
              </div>
              <div className={styles.inputGroup}>
                <label>상세 내용</label>
                <textarea
                  className={styles.input}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  readOnly={isViewMode}
                />
              </div>
              <div className={styles.modalFooter}>
                {isViewMode ? (
                  <>
                    <button
                      type="button"
                      className={styles.submitBtn}
                      onClick={(e) => {
                        e.preventDefault();
                        setIsViewMode(false);
                      }}
                    >
                      수정하기
                    </button>
                    <button
                      type="button"
                      className={styles.cancelBtn}
                      onClick={() => handleDeleteTask(editingId!)}
                    >
                      삭제하기
                    </button>
                  </>
                ) : (
                  <>
                    <button type="submit" className={styles.submitBtn}>
                      저장
                    </button>
                    <button
                      type="button"
                      className={styles.cancelBtn}
                      onClick={resetFormAndClose}
                    >
                      취소
                    </button>
                  </>
                )}
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskCreatePage;
