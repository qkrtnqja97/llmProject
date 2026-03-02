/* src/context/AuthContext.tsx */
import {
  createContext,
  useContext,
  useState,
  ReactNode,
  useEffect,
} from "react";
import { authService } from "@services/authService";
import { userService } from "@services/userService";

interface AuthContextType {
  user: string | null;
  userSettings: any;
  login: (id: string, pw: string) => Promise<boolean>;
  logout: () => void;
  isInitialized: boolean;
  updateLocalSettings: (newSettings: any) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<string | null>(null);
  const [userSettings, setUserSettings] = useState<any>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // --- 테마 적용 로직 통합 관리 (3종 테마 대응) ---
  const applyTheme = (theme: string) => {
    // 특정 테마(light/dark)로 강제 고정하던 삼항 연산자를 제거하고
    // 들어온 테마값(navy, gray, forest 등)을 그대로 반영합니다.
    const targetTheme = theme || "navy";
    document.documentElement.setAttribute("data-theme", targetTheme);
    localStorage.setItem("theme", targetTheme);
  };

  const fetchAndApplySettings = async () => {
    try {
      const settings = await userService.getSettings();
      console.log("--- 계정 설정 데이터 로드 성공 ---");
      setUserSettings(settings);

      // DB에서 가져온 테마를 즉시 적용 (실시간 반영의 핵심)
      if (settings?.theme) {
        applyTheme(settings.theme);
      }
      return settings;
    } catch (error) {
      console.error("설정 로드 실패:", error);
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      // 1. 서비스 접속 시 로컬 스토리지 테마부터 즉시 적용
      const lastTheme = localStorage.getItem("theme") || "navy";
      applyTheme(lastTheme);

      const savedUser = localStorage.getItem("user_id");
      if (savedUser) {
        setUser(savedUser);
        await fetchAndApplySettings();
      }
      setIsInitialized(true);
    };
    initAuth();
  }, []);

  const login = async (emp_id: string, password: string) => {
    try {
      const data = await authService.login(emp_id, password);
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("user_id", emp_id);

      setUser(emp_id);
      await fetchAndApplySettings();
      return true;
    } catch (error: any) {
      const message = error.response?.data?.detail || "로그인에 실패했습니다.";
      alert(message);
      return false;
    }
  };

  const logout = () => {
    if (window.confirm("로그아웃 하시겠습니까?")) {
      setUser(null);
      setUserSettings(null);
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_id");

      // 로그아웃 시에도 마지막 테마 설정을 유지하기 위해 테마 초기화 로직은 제외합니다.
      window.location.href = "/";
    }
  };

  const updateLocalSettings = (newSettings: any) => {
    setUserSettings((prev: any) => {
      if (JSON.stringify(prev) === JSON.stringify(newSettings)) {
        return prev;
      }
      return newSettings;
    });

    // 세팅 모달에서 설정값이 바뀔 때(특히 테마) 즉각 HTML 속성을 업데이트합니다.
    if (newSettings?.theme) {
      applyTheme(newSettings.theme);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        userSettings,
        login,
        logout,
        isInitialized,
        updateLocalSettings,
      }}
    >
      {isInitialized ? (
        children
      ) : (
        <div
          style={{
            background: "var(--bg-main)",
            color: "var(--text-main)",
            height: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          인증 정보 로딩 중...
        </div>
      )}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};
