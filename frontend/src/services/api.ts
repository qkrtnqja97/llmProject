// src/services/api.ts
const BASE_URL = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export const authApi = {
  login: async (emp_id: string, pass: string) => {
    const response = await fetch(`${BASE_URL}/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ emp_id, password: pass }),
    });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "로그인 실패");
    }
    return response.json();
  },
};

export const chatApi = {
  askLLM: async (question: string) => {
    const response = await fetch(`${BASE_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!response.ok) throw new Error("서버 응답 오류");
    return response.json();
  },

  // ✅ ChatContext에서 호출하는 mockSendMessage 추가
  mockSendMessage: async (text: string): Promise<string> => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return `[Mock 응답] ${text}에 대한 답변입니다.`;
  },
};
