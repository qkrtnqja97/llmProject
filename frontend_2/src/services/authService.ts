// src/services/authService.ts
import apiClient from "./apiClient";

export const authService = {
  login: async (emp_id: string, password: string) => {
    // 백엔드 UserLogin 스키마와 일치하는 페이로드 전달
    const response = await apiClient.post("/auth/login", {
      emp_id,
      password,
    });
    return response.data; // { access_token: "...", token_type: "bearer" }
  },

  // 필요 시 회원가입 등 추가 가능
  register: async (payload: {
    emp_id: string;
    password: string;
    name: string;
  }) => {
    const response = await apiClient.post("/auth/register", payload);
    return response.data;
  },
};
