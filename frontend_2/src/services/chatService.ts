import axios from "axios";

// 백엔드 주소
const API_BASE_URL = "http://localhost:8000/v1";

export const chatService = {
	/**
	 * @param prompt 사용자 질문
	 * @param userId 사용자 식별값 (이메일 혹은 ID)
	 */
	async ask(prompt: string, userId: string) {
		// 로컬스토리지에서 토큰 가져오기
		const token = localStorage.getItem("access_token") || "";

		const response = await axios.post(
			`${API_BASE_URL}/chat`,
			{
				user_id: userId, // 백엔드 요구사항: 사용자 ID
				session_id: token, // 백엔드 요구사항: 세션 ID (토큰으로 대체)
				prompt: prompt, // 백엔드 요구사항: 질문 내용
			},
			{
				headers: {
					Authorization: `Bearer ${token}`, // 인증 헤더 유지
				},
			},
		);

		return response.data; // ChatResponse { "response": "..." }
	},
};
