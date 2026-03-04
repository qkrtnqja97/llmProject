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

  // 📍 텍스트에서 표 데이터를 추출하여 차트용 배열로 만드는 함수
  const parseChartData = (content: string) => {
    const lines = content.split("\n");
    const chartData: any[] = [];

    // 표 형식 (| 월 | 매출 |)을 찾는 정규식
    const tableRowRegex = /^\|?\s*(\d+월)\s*\|\s*([\d,]+)원?\s*\|?$/;

    lines.forEach((line) => {
      const match = line.match(tableRowRegex);
      if (match) {
        const name = match[1]; // "1월"
        const value = parseInt(match[2].replace(/,/g, "")); // "272,308,310" -> 272308310
        chartData.push({ name, value });
      }
    });

    return chartData.length > 0 ? chartData : null;
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
                        {/* ✅ 마크다운 렌더링 (표 출력 가능) */}
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
                              padding: 10,
                              borderRadius: 8,
                            }}
                          >
                            <p
                              style={{
                                fontSize: "12px",
                                fontWeight: "bold",
                                marginBottom: "10px",
                                color: "#333",
                              }}
                            >
                              📊 데이터 시각화
                            </p>
                            <ResponsiveContainer width="100%" height="100%">
                              <BarChart data={chartData}>
                                <CartesianGrid
                                  strokeDasharray="3 3"
                                  vertical={false}
                                />
                                <XAxis dataKey="name" fontSize={12} />
                                <YAxis hide />
                                <Tooltip
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
