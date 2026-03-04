/* src/components/chats/ChatPanel.tsx */
import React, { useState, useRef, useEffect } from "react";
import { useChat } from "@context/ChatContext";
import { useAuth } from "@context/AuthContext";
import { User, Bot, Send } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import styles from "./ChatPanel.module.css";

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

  /**
   * 📍 텍스트에서 데이터를 추출하여 차트용 배열로 만드는 함수 (보강됨)
   */
  const parseChartData = (content: string) => {
    const lines = content.split("\n");
    const chartData: any[] = [];

    // 1. 표 형식 인식: | 1월 | 272,308,310 |
    const tableRowRegex = /^\|?\s*(\d+월)\s*\|\s*([\d,]+)\s*원?\s*\|?$/;
    // 2. 리스트 형식 인식: 1월: 272,308,310 (원 단위가 없어도 인식하도록 수정)
    const listRowRegex = /^[-*•]?\s*(\d+월)[:\s-]+\s*([\d,]+)\s*(?:원)?/;

    lines.forEach((line) => {
      const trimmedLine = line.trim();
      const match =
        trimmedLine.match(tableRowRegex) || trimmedLine.match(listRowRegex);

      if (match) {
        const name = match[1]; // "1월"
        // 콤마(,)를 모두 제거하고 순수하게 숫자만 추출
        const value = parseInt(match[2].replace(/,/g, ""));

        if (!isNaN(value)) {
          chartData.push({ name, value });
        }
      }
    });

    // 월 순서대로 정렬 (1월 -> 12월)
    const sortedData = chartData.sort((a, b) => {
      const aNum = parseInt(a.name);
      const bNum = parseInt(b.name);
      return aNum - bNum;
    });

    return sortedData.length > 0 ? sortedData : null;
  };

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
          const chartData =
            msg.role === "assistant" ? parseChartData(msg.content) : null;

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

                        {/* ✅ 차트 데이터가 있으면 그래프 추가 렌더링 */}
                        {chartData && (
                          <div
                            className={styles.chartWrapper}
                            style={{
                              width: "100%",
                              height: 250,
                              marginTop: 20,
                              background: "#fff",
                              padding: "15px 10px 10px 10px",
                              borderRadius: 8,
                              border: "1px solid #eee",
                            }}
                          >
                            <p
                              style={{
                                fontSize: "12px",
                                fontWeight: "bold",
                                marginBottom: "15px",
                                color: "#333",
                                display: "flex",
                                alignItems: "center",
                                gap: "5px",
                              }}
                            >
                              📊 데이터 시각화 리포트
                            </p>
                            <ResponsiveContainer width="100%" height="100%">
                              <BarChart
                                data={chartData}
                                margin={{
                                  top: 5,
                                  right: 5,
                                  left: -20,
                                  bottom: 5,
                                }}
                              >
                                <CartesianGrid
                                  strokeDasharray="3 3"
                                  vertical={false}
                                  stroke="#f0f0f0"
                                />
                                <XAxis
                                  dataKey="name"
                                  fontSize={11}
                                  tickLine={false}
                                  axisLine={false}
                                />
                                <YAxis hide />
                                <Tooltip
                                  cursor={{ fill: "#f5f5ff" }}
                                  contentStyle={{
                                    borderRadius: "8px",
                                    border: "none",
                                    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                                  }}
                                  formatter={(value: any) =>
                                    new Intl.NumberFormat("ko-KR").format(
                                      Number(value),
                                    ) + "원"
                                  }
                                />
                                <Bar
                                  dataKey="value"
                                  fill="#4f46e5"
                                  radius={[4, 4, 0, 0]}
                                  barSize={20}
                                />
                              </BarChart>
                            </ResponsiveContainer>
                          </div>
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
