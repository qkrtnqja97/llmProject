// src/services/apiClient.ts
import axios from "axios";

// 📍 전역 변수로 알람 표시 상태 관리 (파일이 로드될 때 한 번만 생성됨)
let isAuthAlertShown = false;

const apiClient = axios.create({
	baseURL: "http://192.168.0.100:8000/v1",
	headers: {
		"Content-Type": "application/json",
	},
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
			// 📍 이미 알람이 떴다면 추가 실행 방지
			if (!isAuthAlertShown) {
				isAuthAlertShown = true; // 깃발 올리기

				// 로컬 스토리지 비우기
				localStorage.removeItem("access_token");
				localStorage.removeItem("user_id");

				console.error("인증 만료됨. 로그아웃 처리합니다.");

				// 사용자 알림 및 페이지 새로고침
				alert("세션이 만료되었습니다. 다시 로그인해 주세요.");

				// 페이지 이동 또는 새로고침
				window.location.href = "/";

				// (선택 사항) 새로고침이 아닌 경우를 대비해 일정 시간 후 깃발 내리기
				// setTimeout(() => { isAuthAlertShown = false; }, 5000);
			}
		}
		return Promise.reject(error);
	},
);

export default apiClient;
