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

  // --- 테마 적용 로직 ---
  const applyTheme = (theme: string) => {
    const targetTheme = theme || "navy";
    document.documentElement.setAttribute("data-theme", targetTheme);
    localStorage.setItem("theme", targetTheme);
  };

  const fetchAndApplySettings = async () => {
    try {
      const settings = await userService.getSettings();
      console.log("--- 계정 설정 데이터 로드 성공 ---");
      setUserSettings(settings);

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
      try {
        // 1. 테마 먼저 적용
        const lastTheme = localStorage.getItem("theme") || "navy";
        applyTheme(lastTheme);

        // 2. 저장된 유저 정보 확인
        const savedUser = localStorage.getItem("user_id");
        if (savedUser) {
          setUser(savedUser);
          // 서버 응답이 없어도 여기서 멈추지 않도록 catch 처리
          await fetchAndApplySettings().catch((err) => {
            console.error("초기 설정 로드 실패 (무시하고 진행):", err);
          });
        }
      } catch (error) {
        console.error("인증 초기화 에러:", error);
      } finally {
        // 📍 핵심: 에러가 나더라도 무조건 로딩 상태를 해제함
        setIsInitialized(true);
      }
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
      window.location.href = "/";
    }
  };

  // 📍 [핵심 수정] 기존 설정을 유지하며 새로운 설정만 덮어쓰는 로직
  const updateLocalSettings = (newSettings: any) => {
    setUserSettings((prev: any) => {
      // 1. 기존 값(prev)과 새로운 값(newSettings)을 병합합니다.
      // 이를 통해 userSettings 내부에 들어있던 관리자 ID, 권한, 부서 정보 등이 유지됩니다.
      const merged = { ...prev, ...newSettings };

      // 2. 변경사항이 실제로 있을 때만 상태를 업데이트하여 불필요한 리렌더링 방지
      if (JSON.stringify(prev) === JSON.stringify(merged)) {
        return prev;
      }
      return merged;
    });

    // 테마 설정이 포함된 경우 즉시 브라우저에 반영
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
