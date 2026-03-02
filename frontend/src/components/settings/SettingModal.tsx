import React from "react";
import { useSettings } from "../../context/SettingContext";
import styles from "./SettingModal.module.css";

interface SettingsModalProps {
  onClose: () => void;
}

const SettingsModal: React.FC<SettingsModalProps> = ({ onClose }) => {
  const { settings, updateSettings } = useSettings();

  // 스위치 영역 어디를 클릭해도 전환되는 함수
  const handleToggle = () => {
    updateSettings({
      ...settings,
      theme: settings.theme === "light" ? "dark" : "light",
    });
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>시스템 설정</h2>
          <button className={styles.closeXBtn} onClick={onClose}>
            ✕
          </button>
        </div>

        <div className={styles.modalBody}>
          {/* 1. 테마 스위치 섹션 */}
          <section className={styles.configSection}>
            <label className={styles.sectionLabel}>화면 모드</label>
            <div className={styles.themeSwitchContainer} onClick={handleToggle}>
              {/* 슬라이딩 인디케이터 */}
              <div
                className={`${styles.activeIndicator} ${
                  settings.theme === "dark" ? styles.activeIndicatorDark : ""
                }`}
              />

              <div
                className={`${styles.themeOption} ${settings.theme === "light" ? styles.themeOptionActive : ""}`}
              >
                ☀️ Light
              </div>
              <div
                className={`${styles.themeOption} ${settings.theme === "dark" ? styles.themeOptionActive : ""}`}
              >
                🌙 Dark
              </div>
            </div>
          </section>

          {/* 2. 시작 페이지 섹션 */}
          <section className={styles.configSection}>
            <label className={styles.sectionLabel}>기본 시작 페이지</label>
            <select
              className={styles.configSelect}
              value={settings.startPage}
              onChange={(e) =>
                updateSettings({ ...settings, startPage: e.target.value })
              }
            >
              {settings.sidebarMenus
                .filter((m) => m.isVisible)
                .map((m) => (
                  <option key={m.id} value={m.path}>
                    {m.label}
                  </option>
                ))}
            </select>
            <span className={styles.helperText}>
              로그인 후 처음으로 표시될 화면을 선택합니다.
            </span>
          </section>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;
