import React, { createContext, useContext, useState, useCallback } from "react";
import { authApi } from "../services/api";

// ✅ 1. 유저 정보 타입 정의
interface User {
  empId: string;
  name: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null; // ✅ 2. 유저 상태 타입 추가
  isLoading: boolean;
  login: (empId: string, pass: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [isAuthenticated, setIsAuthenticated] = useState(
    !!localStorage.getItem("accessToken"),
  );

  // ✅ 3. 유저 정보를 저장할 상태 추가 (초기값은 로컬스토리지 활용 가능)
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem("user");
    return saved ? JSON.parse(saved) : null;
  });

  const [isLoading, setIsLoading] = useState(false);

  const login = useCallback(async (empId: string, pass: string) => {
    setIsLoading(true);
    try {
      const data = await authApi.login(empId, pass);

      // ✅ 4. 서버 응답 데이터에 따라 유저 정보 저장 (data 구조에 맞춰 수정 필요)
      // 만약 API에서 유저 이름을 주지 않는다면 임시로 empId를 이름으로 쓸 수도 있습니다.
      const userData = {
        empId: empId,
        name: data.name || "관리자", // API 응답에 name이 있다면 사용
      };

      localStorage.setItem("accessToken", data.access_token);
      localStorage.setItem("user", JSON.stringify(userData)); // 로컬스토리지 저장

      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("user"); // ✅ 유저 정보 삭제
    setUser(null);
    setIsAuthenticated(false);
  };

  // ✅ 5. Provider value에 user 추가
  return (
    <AuthContext.Provider
      value={{ isAuthenticated, user, isLoading, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth error");
  return context;
};
