// src/shared/components/LayoutSettings.tsx
import React, { useState } from "react";
import { useLayout } from "../app/providers/LayoutProviders.tsx";
import type { LayoutTheme } from "../shared/types/layout.tsx";

interface LayoutSettingsProps {
  onClose: () => void;
}

export const LayoutSettings: React.FC<LayoutSettingsProps> = ({ onClose }) => {
  const { menu, options, addMenuItem, updateMenuItem, removeMenuItem, setOptions } = useLayout();
  const [newLabel, setNewLabel] = useState("");
  const [newPath, setNewPath] = useState("");

  const handleAdd = () => {
    if (!newLabel.trim() || !newPath.trim()) return;
    addMenuItem({ label: newLabel.trim(), path: newPath.trim() });
    setNewLabel("");
    setNewPath("");
  };

  const handleThemeChange = (theme: LayoutTheme) => {
    setOptions((prev) => ({ ...prev, theme }));
  };

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
      <div className="w-[480px] max-h-[80vh] bg-white rounded-2xl shadow-xl p-6 flex flex-col gap-4">
        <div className="flex justify-between items-center">
          <h2 className="font-semibold text-lg">레이아웃 / 메뉴 설정</h2>
          <button onClick={onClose} className="text-zinc-500 hover:text-zinc-900">
            ✕
          </button>
        </div>

        {/* 테마 옵션 */}
        <section>
          <h3 className="text-sm font-medium mb-2">테마</h3>
          <div className="flex gap-2 text-xs">
            {(["auto", "light", "dark"] as LayoutTheme[]).map((t) => (
              <button
                key={t}
                onClick={() => handleThemeChange(t)}
                className={`px-3 py-1 rounded-full border ${
                  options.theme === t ? "bg-black text-white" : "bg-white text-zinc-700"
                }`}
              >
                {t === "auto" ? "시스템" : t === "light" ? "라이트" : "다크"}
              </button>
            ))}
          </div>
        </section>

        {/* 메뉴 리스트 */}
        <section className="flex-1 overflow-auto border rounded-xl p-3 space-y-2">
          <h3 className="text-sm font-medium mb-2">메뉴</h3>
          {menu.map((item) => (
            <div
              key={item.id}
              className="flex items-center gap-2 text-xs border rounded-lg px-2 py-1"
            >
              <input
                className="flex-1 border-none outline-none bg-transparent"
                value={item.label}
                onChange={(e) =>
                  updateMenuItem(item.id, {
                    label: e.target.value,
                  })
                }
              />
              {!item.pinned && (
                <button
                  className="text-red-500 text-[11px]"
                  onClick={() => removeMenuItem(item.id)}
                >
                  삭제
                </button>
              )}
            </div>
          ))}
        </section>

        {/* 새 메뉴 추가 */}
        <section className="space-y-2">
          <h3 className="text-sm font-medium">새 카테고리 추가</h3>
          <div className="flex gap-2">
            <input
              className="flex-1 border rounded-lg px-2 py-1 text-xs"
              placeholder="메뉴 이름 (예: 고객 문의)"
              value={newLabel}
              onChange={(e) => setNewLabel(e.target.value)}
            />
          </div>
          <div className="flex gap-2">
            <input
              className="flex-1 border rounded-lg px-2 py-1 text-xs"
              placeholder="경로 (예: /tickets)"
              value={newPath}
              onChange={(e) => setNewPath(e.target.value)}
            />
            <button
              className="px-3 py-1 text-xs rounded-lg bg-black text-white"
              onClick={handleAdd}
            >
              추가
            </button>
          </div>
        </section>
      </div>
    </div>
  );
};