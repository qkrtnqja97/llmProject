import apiClient from "./apiClient";

export interface TaskCreateInput {
  title: string;
  content?: string;
  priority: string;
  due_date?: string | null;
  status: string;
}

export const workService = {
  // 기존 메서드
  createTask: async (data: TaskCreateInput) => {
    const response = await apiClient.post("/work/", data);
    return response.data;
  },

  getTasks: async (skip = 0, limit = 50) => {
    const response = await apiClient.get(`/work/?skip=${skip}&limit=${limit}`);
    return response.data; // { total: number, items: any[] } 형태 반환 가정
  },

  // 🚀 누락된 메서드 추가
  updateTask: async (id: number, data: TaskCreateInput) => {
    const response = await apiClient.put(`/work/${id}`, data);
    return response.data;
  },

  deleteTask: async (id: number) => {
    const response = await apiClient.delete(`/work/${id}`);
    return response.data;
  },
};
