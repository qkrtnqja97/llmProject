// src/services/apiClient.ts
import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://192.168.0.100:8000/v1", // 백엔드 서버 주소 및 API 버전
  headers: {
    "Content-Type": "application/json",
  },
});

// 요청 인터셉터: 로컬 스토리지에 토큰이 있다면 모든 요청 헤더에 주입
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답 인터셉터 (에러 감지)
apiClient.interceptors.response.use(
  (response) => response, // 성공 시 그대로 반환
  (error) => {
    // 401 에러(Unauthorized)가 발생하면 토큰이 만료되었거나 없는 경우임
    if (error.response && error.response.status === 401) {
      // 로컬 스토리지 비우기
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_id");

      console.error("인증 만료됨. 로그아웃 처리합니다.");

      // 사용자에게 알리고 페이지를 새로고침하여 AuthProvider가 상태를 재체크하게 함
      // 결과적으로 HomePage의 useEffect가 작동하여 로그인 팝업이 다시 뜨게 됩니다.
      alert("세션이 만료되었습니다. 다시 로그인해 주세요.");
      window.location.reload();
    }
    return Promise.reject(error);
  },
);

export default apiClient;
