import React, {
  createContext,
  useState,
  useContext,
  useEffect,
  useCallback,
} from "react";

export type Theme = "navy" | "gray" | "sand";

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const VALID_THEMES: Theme[] = ["navy", "gray", "sand"];
const DEFAULT_THEME: Theme = "navy";
const THEME_STORAGE_KEY = "theme";

/**
 * 저장된 테마를 안전하게 가져오는 유틸리티
 */
export const getSavedTheme = (): Theme => {
  if (typeof window === "undefined") return DEFAULT_THEME;
  const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) as Theme;
  return VALID_THEMES.includes(savedTheme) ? savedTheme : DEFAULT_THEME;
};

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [theme, setThemeState] = useState<Theme>(getSavedTheme);

  // 테마 적용 핵심 로직 (재사용성을 위해 useCallback 사용)
  const applyTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem(THEME_STORAGE_KEY, newTheme);

    // 이전 번역 페이지 기조 유지: 불필요한 인라인 스타일 제거
    document.documentElement.style.removeProperty("background-color");
  }, []);

  const toggleTheme = () => {
    const currentIndex = VALID_THEMES.indexOf(theme);
    const nextTheme = VALID_THEMES[(currentIndex + 1) % VALID_THEMES.length];
    applyTheme(nextTheme);
  };

  // 초기 로드 시 한 번 실행
  useEffect(() => {
    const initialTheme = getSavedTheme();
    applyTheme(initialTheme);
  }, [applyTheme]);

  const value: ThemeContextType = {
    theme,
    setTheme: applyTheme,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};
