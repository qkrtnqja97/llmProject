import axios from "axios";

// 백엔드 주소 (설정에 따라 변경)
const API_BASE_URL = "http://192.168.0.100:8000/v1";

export const chatService = {
  async ask(prompt: string) {
    // 로컬스토리지에서 토큰 가져오기 (인증용)
    const token = localStorage.getItem("access_token");

    const response = await axios.post(
      `${API_BASE_URL}/chat`,
      { prompt }, // 백엔드 ChatRequest 스키마와 일치
      {
        headers: {
          Authorization: `Bearer ${token}`, // 인증이 필요한 경우
        },
      },
    );
    return response.data; // 백엔드 ChatResponse { "response": "..." }
  },
};
