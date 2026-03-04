/* src/services/apiClient.ts */
import axios from "axios";

// 📍 전역 변수로 알람 표시 상태 관리
let isAuthAlertShown = false;

const apiClient = axios.create({
  // 📍 백엔드 로그에 찍힌 실제 IP 주소(176)로 수정하세요.
  // 만약 로컬에서만 테스트한다면 "http://localhost:8000/v1"도 가능합니다.
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 60000, // 로그인/기본 요청은 10초 내외로 설정
});

// 요청 인터셉터
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답 인터셉터
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // 401 에러(Unauthorized) 감지
    if (error.response && error.response.status === 401) {
      if (!isAuthAlertShown) {
        isAuthAlertShown = true;

        // 로컬 스토리지 비우기
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_id");

        console.error("인증 만료됨. 로그아웃 처리합니다.");
        alert("세션이 만료되었습니다. 다시 로그인해 주세요.");

        // 메인 페이지로 이동
        window.location.href = "/";
      }
    }
    return Promise.reject(error);
  },
);

export default apiClient;
