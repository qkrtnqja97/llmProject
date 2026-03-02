// src/services/userService.ts
import apiClient from "./apiClient";

export const userService = {
  getSettings: async () => {
    const response = await apiClient.get("/user/settings");
    return response.data;
  },

  updateSettings: async (payload: any) => {
    const response = await apiClient.post("/user/settings", payload);
    return response.data;
  },
};
