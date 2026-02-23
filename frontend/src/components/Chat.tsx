import React, { useState } from "react";

const API_URL = "http://192.168.0.243:8000/v1/";  // 또는 ipconfig로 확인한 진짜 IP

export default function Chat() {
  const [value, setValue] = useState("");
  const [answer, setAnswer] = useState("");

  const handleClick = async () => {
    if (!value.trim()) return;

    console.log("🟢 handleClick 호출됨, value:", value);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: value,
        }),
      });

      console.log("📡 status:", response.status);

      if (!response.ok) {
        console.error("❌ API 에러:", response.statusText);
        setAnswer("API 에러 발생: " + response.statusText);
        return;
      }

      const data = await response.json();
      console.log("✅ data:", data);

      setAnswer(data.response ?? "응답이 비어 있어요 ㅠㅠ");
      setValue("");
    } catch (err) {
      console.error("🌋 네트워크 에러:", err);
      setAnswer("네트워크 에러 발생");
    }
  };

  return (
    <div className="chat-card">
      <h2 className="chat-card__title">무엇을 도와드릴까요?</h2>

      <div className="chat-card__form">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          className="chat-card__input"
          placeholder="질문을 입력하세요"
        />
        <button
          className="chat-card__button"
          type="button"
          onClick={handleClick}
        >
          보내기
        </button>
      </div>

      {answer && (
        <div className="mt-6">
          <p className="text-gray-500 text-sm mb-1">검색 결과</p>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}
<h1 style={{ color: "red" }}>여기 Chat.tsx임</h1>