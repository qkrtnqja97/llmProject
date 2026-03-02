import React, { createContext, useContext, useState, useEffect } from "react";
import { useAuth } from "./AuthContext";

interface MenuItem {
  id: string;
  label: string;
  path: string;
  isVisible: boolean;
  icon: string;
}

interface UserSettings {
  theme: "light" | "dark";
  startPage: string;
  sidebarMenus: MenuItem[];
}

interface SettingsContextType {
  settings: UserSettings;
  updateSettings: (newSettings: UserSettings) => Promise<void>;
  isLoading: boolean;
}

const defaultMenus: MenuItem[] = [
  {
    id: "ai",
    label: "AI 업무 검색",
    path: "/ai",
    isVisible: true,
    icon: "🔍",
  },
  {
    id: "dashboard",
    label: "대시보드",
    path: "/dashboard",
    isVisible: true,
    icon: "📊",
  },
  {
    id: "tasks",
    label: "업무 작성",
    path: "/tasks",
    isVisible: true,
    icon: "📝",
  },
  {
    id: "inventory",
    label: "재고 관리",
    path: "/inventory",
    isVisible: true,
    icon: "📦",
  },
  {
    id: "orders",
    label: "발주 관리",
    path: "/orders",
    isVisible: true,
    icon: "🛒",
  },
  {
    id: "products",
    label: "제품 관리",
    path: "/products",
    isVisible: true,
    icon: "🛠️",
  },
  {
    id: "contacts",
    label: "연락처",
    path: "/contacts",
    isVisible: true,
    icon: "👥",
  },
  {
    id: "library",
    label: "자료실",
    path: "/library",
    isVisible: true,
    icon: "📂",
  },
  {
    id: "history",
    label: "검색 기록",
    path: "/history",
    isVisible: true,
    icon: "📜",
  },
  {
    id: "company-settings",
    label: "시스템 환경 설정",
    path: "/company",
    icon: "🏢",
    isVisible: true,
  },
];

const SettingsContext = createContext<SettingsContextType | undefined>(
  undefined,
);

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { user, isAuthenticated } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [settings, setSettings] = useState<UserSettings>({
    theme: "light",
    startPage: "/",
    sidebarMenus: defaultMenus,
  });

  useEffect(() => {
    const fetchSettings = async () => {
      if (!isAuthenticated || !user?.empId) {
        setIsLoading(false);
        return;
      }
      try {
        const response = await fetch(
          `http://localhost:8000/v1/user/settings/${user.empId}`,
        );
        if (response.ok) {
          const data: UserSettings = await response.json();

          // ✅ [병합 로직 추가] DB 데이터와 defaultMenus 비교
          // 서버에 저장된 메뉴들 중 defaultMenus에 정의된 최신 정보(아이콘, 이름 등)를 유지하며 병합
          const mergedMenus = defaultMenus.map((dMenu) => {
            const savedMenu = data.sidebarMenus?.find(
              (sMenu) => sMenu.id === dMenu.id,
            );
            if (savedMenu) {
              // 노출 여부(isVisible)만 서버 설정을 따르고, 나머지는 최신 코드(defaultMenus) 기준 유지
              return { ...dMenu, isVisible: savedMenu.isVisible };
            }
            return dMenu; // 서버에 없는 새 메뉴는 그대로 추가
          });

          setSettings({
            ...data,
            sidebarMenus: mergedMenus,
          });
          document.documentElement.setAttribute("data-theme", data.theme);
        }
      } catch (error) {
        console.error("설정 로드 실패:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchSettings();
  }, [isAuthenticated, user]);

  const updateSettings = async (newSettings: UserSettings) => {
    setSettings(newSettings);
    document.documentElement.setAttribute("data-theme", newSettings.theme);

    if (user?.empId) {
      try {
        await fetch(`http://localhost:8000/v1/user/settings/${user.empId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(newSettings),
        });
      } catch (error) {
        console.error("설정 저장 실패:", error);
      }
    }
  };

  return (
    <SettingsContext.Provider value={{ settings, updateSettings, isLoading }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context)
    throw new Error("useSettings는 SettingsProvider 안에서만 사용 가능합니다.");
  return context;
};
