/* src/components/chats/ChatPanel.tsx */
import React, { useState, useRef, useEffect } from "react";
import { useChat } from "@context/ChatContext";
import type { ChartInfo } from "@context/ChatContext";
import { useAuth } from "@context/AuthContext";
import { User, Bot, Send } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  ResponsiveContainer,
  ComposedChart,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import styles from "./ChatPanel.module.css";

// ─────────────────────────────────────────────
// 차트 색상 팔레트
// ─────────────────────────────────────────────
const COLORS = ["#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

// ─────────────────────────────────────────────
// 숫자 포맷터 (Tooltip용)
// ─────────────────────────────────────────────
const formatValue = (value: unknown) => {
  const n = Number(value);
  if (isNaN(n)) return String(value);
  return new Intl.NumberFormat("ko-KR").format(n);
};

// ─────────────────────────────────────────────
// 테이블 렌더러
// ─────────────────────────────────────────────
const TableView: React.FC<{ data: Record<string, unknown>[] }> = ({ data }) => {
  if (!data || data.length === 0) return null;
  const cols = Object.keys(data[0]);
  return (
    <div style={{ overflowX: "auto", marginTop: 12 }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
        <thead>
          <tr>
            {cols.map((col) => (
              <th
                key={col}
                style={{
                  padding: "6px 10px",
                  background: "#f0f0f8",
                  borderBottom: "1px solid #ddd",
                  textAlign: "left",
                  whiteSpace: "nowrap",
                }}
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} style={{ background: i % 2 === 0 ? "#fff" : "#fafafa" }}>
              {cols.map((col) => (
                <td
                  key={col}
                  style={{
                    padding: "5px 10px",
                    borderBottom: "1px solid #eee",
                    whiteSpace: "nowrap",
                  }}
                >
                  {row[col] === null || row[col] === undefined
                    ? "-"
                    : typeof row[col] === "number"
                    ? formatValue(row[col])
                    : String(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// ─────────────────────────────────────────────
// 메인 ChartRenderer
// ─────────────────────────────────────────────
const ChartRenderer: React.FC<{ chartInfo: ChartInfo }> = ({ chartInfo }) => {
  const { type, title, xKey, dataKeys = [], data = [], useSecondaryAxis = false, yAxes = {} } = chartInfo;

  if (type === "none" || !data.length || !xKey) return null;

  if (type === "table") {
    return (
      <div style={{ marginTop: 16, padding: "12px 14px", background: "#fff", borderRadius: 8, border: "1px solid #eee" }}>
        <p style={{ fontSize: 12, fontWeight: "bold", marginBottom: 8, color: "#333" }}>📋 {title || "데이터 테이블"}</p>
        <TableView data={data} />
      </div>
    );
  }

  const chartHeight = 240;

  // ── Dual Y-Axis (ComposedChart) ──────────────────────────────
  if (useSecondaryAxis && dataKeys.length > 1) {
    const primaryKeys = dataKeys.filter((k) => !yAxes[k] || yAxes[k] === "primary");
    const secondaryKeys = dataKeys.filter((k) => yAxes[k] === "secondary");

    return (
      <div style={{ marginTop: 16, padding: "12px 14px", background: "#fff", borderRadius: 8, border: "1px solid #eee" }}>
        <p style={{ fontSize: 12, fontWeight: "bold", marginBottom: 8, color: "#333" }}>📊 {title || "데이터 시각화"}</p>
        <ResponsiveContainer width="100%" height={chartHeight}>
          <ComposedChart data={data} margin={{ top: 4, right: 20, left: -10, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
            <XAxis dataKey={xKey} fontSize={11} tickLine={false} axisLine={false} />
            <YAxis yAxisId="primary" fontSize={11} tickLine={false} axisLine={false} tickFormatter={formatValue} />
            <YAxis yAxisId="secondary" orientation="right" fontSize={11} tickLine={false} axisLine={false} tickFormatter={formatValue} />
            <Tooltip
              contentStyle={{ borderRadius: 8, border: "none", boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}
              formatter={(val: unknown, name: string) => [formatValue(val), name]}
            />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            {primaryKeys.map((k, i) =>
              type === "line" ? (
                <Line yAxisId="primary" key={k} type="monotone" dataKey={k} stroke={COLORS[i % COLORS.length]} dot={false} strokeWidth={2} />
              ) : (
                <Bar yAxisId="primary" key={k} dataKey={k} fill={COLORS[i % COLORS.length]} radius={[3, 3, 0, 0]} barSize={18} />
              )
            )}
            {secondaryKeys.map((k, i) =>
              type === "line" ? (
                <Line yAxisId="secondary" key={k} type="monotone" dataKey={k} stroke={COLORS[(primaryKeys.length + i) % COLORS.length]} dot={false} strokeWidth={2} strokeDasharray="4 2" />
              ) : (
                <Bar yAxisId="secondary" key={k} dataKey={k} fill={COLORS[(primaryKeys.length + i) % COLORS.length]} radius={[3, 3, 0, 0]} barSize={18} />
              )
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // ── 꺾은선 차트 (Line) ──────────────────────────────────────
  if (type === "line") {
    return (
      <div style={{ marginTop: 16, padding: "12px 14px", background: "#fff", borderRadius: 8, border: "1px solid #eee" }}>
        <p style={{ fontSize: 12, fontWeight: "bold", marginBottom: 8, color: "#333" }}>📈 {title || "추이 차트"}</p>
        <ResponsiveContainer width="100%" height={chartHeight}>
          <LineChart data={data} margin={{ top: 4, right: 10, left: -10, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
            <XAxis dataKey={xKey} fontSize={11} tickLine={false} axisLine={false} />
            <YAxis fontSize={11} tickLine={false} axisLine={false} tickFormatter={formatValue} />
            <Tooltip
              contentStyle={{ borderRadius: 8, border: "none", boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}
              formatter={(val: unknown, name: string) => [formatValue(val), name]}
            />
            {dataKeys.length > 1 && <Legend wrapperStyle={{ fontSize: 11 }} />}
            {dataKeys.map((k, i) => (
              <Line key={k} type="monotone" dataKey={k} stroke={COLORS[i % COLORS.length]} dot={false} strokeWidth={2} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // ── 막대 차트 (Bar, 기본) ────────────────────────────────────
  return (
    <div style={{ marginTop: 16, padding: "12px 14px", background: "#fff", borderRadius: 8, border: "1px solid #eee" }}>
      <p style={{ fontSize: 12, fontWeight: "bold", marginBottom: 8, color: "#333" }}>📊 {title || "데이터 시각화"}</p>
      <ResponsiveContainer width="100%" height={chartHeight}>
        <BarChart data={data} margin={{ top: 4, right: 10, left: -10, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
          <XAxis dataKey={xKey} fontSize={11} tickLine={false} axisLine={false} />
          <YAxis fontSize={11} tickLine={false} axisLine={false} tickFormatter={formatValue} />
          <Tooltip
            cursor={{ fill: "#f5f5ff" }}
            contentStyle={{ borderRadius: 8, border: "none", boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}
            formatter={(val: unknown, name: string) => [formatValue(val), name]}
          />
          {dataKeys.length > 1 && <Legend wrapperStyle={{ fontSize: 11 }} />}
          {dataKeys.map((k, i) => (
            <Bar key={k} dataKey={k} fill={COLORS[i % COLORS.length]} radius={[3, 3, 0, 0]} barSize={20} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

// ─────────────────────────────────────────────
// ChatPanel 본체
// ─────────────────────────────────────────────
const ChatPanel: React.FC = () => {
  const { messages, sendMessage } = useChat();
  const { user, userSettings } = useAuth();
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;
    const userPrompt = input;
    const userId = (userSettings as any)?.emp_id || user || "guest";
    setInput("");
    setIsTyping(true);

    try {
      await sendMessage(userPrompt, userId, () => {
        setIsTyping(false);
      });
    } catch (error) {
      console.error("전송 에러:", error);
      setIsTyping(false);
    }
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.messageList} ref={scrollRef}>
        {messages.length === 0 && (
          <div className={styles.welcomeSection}>
            <Bot size={56} className={styles.welcomeIcon} />
            <p>
              Biz AI 어시스턴트입니다.
              <br />
              무엇을 도와드릴까요?
            </p>
          </div>
        )}

        {messages.map((msg, idx) => {
          return (
            <div
              key={idx}
              className={`${styles.messageWrapper} ${styles[msg.role]}`}
            >
              <div className={styles.avatar}>
                {msg.role === "user" ? <User size={18} /> : <Bot size={18} />}
              </div>
              <div className={styles.contentWrapper}>
                <div className={styles.senderName}>
                  {msg.role === "user" ? "나" : "AI 비서"}
                </div>
                <div className={styles.bubbleAndInfo}>
                  <div className={styles.bubble}>
                    {msg.role === "assistant" && msg.content === "" ? (
                      <div className={styles.loadingBubble}>
                        <span className={styles.dot}></span>
                        <span className={styles.dot}></span>
                        <span className={styles.dot}></span>
                      </div>
                    ) : (
                      <div className={styles.markdownContent}>
                        {/* 마크다운 렌더링 */}
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content}
                        </ReactMarkdown>

                        {/* ✅ llmServer 시각화 노드가 반환한 chart_info로 차트 렌더링 */}
                        {msg.chartInfo && msg.chartInfo.type !== "none" && (
                          <ChartRenderer chartInfo={msg.chartInfo} />
                        )}
                      </div>
                    )}
                  </div>
                  <span className={styles.timestamp}>{msg.timestamp}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className={styles.inputArea}>
        <div className={styles.inputContainer}>
          <textarea
            placeholder={
              isTyping
                ? "AI가 응답을 생성 중입니다..."
                : "업무에 대해 질문해보세요..."
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey && !isTyping) {
                e.preventDefault();
                handleSend();
              }
            }}
            rows={1}
            disabled={isTyping}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isTyping}
            className={isTyping ? styles.disabledButton : ""}
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
