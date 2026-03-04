/* src/services/chatService.ts */
import axios from "axios";

const API_BASE_URL = "http://localhost:8000/v1";

export const chatService = {
  async ask(prompt: string, userId: string) {
    const token = localStorage.getItem("access_token") || "";

    const response = await axios.post(
      `${API_BASE_URL}/chat`,
      {
        user_id: userId,
        session_id: token,
        prompt: prompt,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      },
    );

    // 백엔드에서 dict로 리턴한 결과는 response.data에 담깁니다.
    return response.data;
  },
};
