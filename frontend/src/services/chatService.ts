/* src/services/chatService.ts */
import apiClient from "./apiClient"; // 📍 기존 axios 대신 이미 설정된 apiClient 사용

export const chatService = {
  async ask(prompt: string, userId: string) {
    // 📍 apiClient는 내부적으로 localStorage에서 token을 가져오도록
    // 이미 interceptor 설정이 되어 있으므로, headers를 따로 넘길 필요가 없습니다.
    const token = localStorage.getItem("access_token") || "";

    const response = await apiClient.post(
      "/chat", // 📍 baseURL이 이미 잡혀있으므로 뒷부분 경로만 작성
      {
        user_id: userId,
        session_id: token,
        prompt: prompt,
      },
    );

    // 백엔드에서 dict로 리턴한 결과는 response.data에 담깁니다.
    return response.data;
  },
};
