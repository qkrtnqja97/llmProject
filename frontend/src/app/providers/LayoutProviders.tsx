// src/app/providers/LayoutProvider.tsx
import React, { createContext, useContext, useEffect, useState } from "react";
import type { LayoutState, LayoutOptions, MenuItem } from "../../shared/types/layout.tsx";
import { loadLayoutState, saveLayoutState, defaultLayoutState } from "../../shared/types/LayoutStorage.ts";

interface LayoutContextValue extends LayoutState {
  setOptions: (updater: (prev: LayoutOptions) => LayoutOptions) => void;
  addMenuItem: (item: Omit<MenuItem, "id">) => void;
  updateMenuItem: (id: string, partial: Partial<MenuItem>) => void;
  removeMenuItem: (id: string) => void;
}

const LayoutContext = createContext<LayoutContextValue | null>(null);

export const LayoutProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<LayoutState>(() => defaultLayoutState);

  // 첫 렌더에서 localStorage에서 불러오기
  useEffect(() => {
    const loaded = loadLayoutState();
    setState(loaded);
  }, []);

  // 변경될 때마다 저장
  useEffect(() => {
    saveLayoutState(state);
  }, [state]);

  const setOptions: LayoutContextValue["setOptions"] = (updater) => {
    setState((prev) => ({
      ...prev,
      options: updater(prev.options),
    }));
  };

  const addMenuItem: LayoutContextValue["addMenuItem"] = (item) => {
    setState((prev) => ({
      ...prev,
      menu: [
        ...prev.menu,
        {
          ...item,
          id: crypto.randomUUID(),
          visible: item.visible ?? true,
        },
      ],
    }));
  };

  const updateMenuItem: LayoutContextValue["updateMenuItem"] = (id, partial) => {
    setState((prev) => ({
      ...prev,
      menu: prev.menu.map((m) => (m.id === id ? { ...m, ...partial } : m)),
    }));
  };

  const removeMenuItem: LayoutContextValue["removeMenuItem"] = (id) => {
    setState((prev) => ({
      ...prev,
      menu: prev.menu.filter((m) => m.id !== id || m.pinned), // pinned는 삭제 방지
    }));
  };

  const value: LayoutContextValue = {
    ...state,
    setOptions,
    addMenuItem,
    updateMenuItem,
    removeMenuItem,
  };

  return <LayoutContext.Provider value={value}>{children}</LayoutContext.Provider>;
};

export function useLayout() {
  const ctx = useContext(LayoutContext);
  if (!ctx) {
    throw new Error("useLayout must be used within LayoutProvider");
  }
  return ctx;
}