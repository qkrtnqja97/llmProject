import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import {
  DragDropContext,
  Droppable,
  Draggable,
  type DropResult,
} from "@hello-pangea/dnd";
import { useAuth } from "../../context/AuthContext";
import { useSettings } from "../../context/SettingContext";
import { useCompany } from "../../context/CompanyContext";
import SettingsModal from "../settings/SettingModal";
import styles from "./Sidebar.module.css";

const Sidebar: React.FC = () => {
  const { user, logout } = useAuth();
  const { settings, updateSettings } = useSettings();
  const { company } = useCompany();

  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showConfig, setShowConfig] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [tempMenus, setTempMenus] = useState(settings.sidebarMenus);

  // --- 이벤트 핸들러 ---
  const handleEditStart = () => {
    setTempMenus([...settings.sidebarMenus]);
    setIsEditing(true);
  };

  const handleEditSave = () => {
    updateSettings({ ...settings, sidebarMenus: tempMenus });
    setIsEditing(false);
  };

  const onDragEnd = (result: DropResult) => {
    if (!result.destination) return;
    const items = [...tempMenus];
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    setTempMenus(items);
  };

  const handleToggleVisible = (id: string) => {
    setTempMenus((prev) =>
      prev.map((m) => (m.id === id ? { ...m, isVisible: !m.isVisible } : m)),
    );
  };

  return (
    <aside
      className={`${styles.sidebar} ${isCollapsed ? styles.collapsed : ""}`}
    >
      {/* [섹션 1] 헤더: 로고 및 접기 버튼 */}
      <div className={styles.header}>
        <div className={styles.brand}>
          <div className={styles.logoBadge}>
            {company.logoUrl ? (
              <img
                src={company.logoUrl}
                alt="Logo"
                className={styles.logoImg}
              />
            ) : (
              (company.name || "B").charAt(0).toUpperCase()
            )}
          </div>
          {!isCollapsed && (
            <span className={styles.companyName}>
              {company.name || "biz ai"}
            </span>
          )}
        </div>
        <button
          className={styles.collapseBtn}
          onClick={() => setIsCollapsed(!isCollapsed)}
        >
          {isCollapsed ? "»" : "«"}
        </button>
      </div>

      {/* [섹션 2] 내비게이션: 스크롤 가능한 메뉴 리스트 */}
      <nav className={styles.nav}>
        <div className={styles.groupHeader}>
          {!isCollapsed && (
            <span className={styles.groupLabel}>사용자 정의 메뉴</span>
          )}
          {!isCollapsed && !isEditing && (
            <button className={styles.inlineEditBtn} onClick={handleEditStart}>
              ⚙️
            </button>
          )}
        </div>

        <DragDropContext onDragEnd={onDragEnd}>
          <Droppable droppableId="menuList" isDropDisabled={!isEditing}>
            {(provided) => (
              <div
                {...provided.droppableProps}
                ref={provided.innerRef}
                className={styles.scrollArea}
              >
                {(isEditing ? tempMenus : settings.sidebarMenus).map(
                  (item, idx) => {
                    if (!isEditing && !item.isVisible) return null;
                    return (
                      <Draggable
                        key={item.id}
                        draggableId={item.id}
                        index={idx}
                        isDragDisabled={!isEditing}
                      >
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className={`${styles.navItemWrapper} ${isEditing ? styles.editing : ""} ${snapshot.isDragging ? styles.dragging : ""}`}
                            onClick={(e) => isEditing && e.preventDefault()} // 편집 시 링크 이동 차단
                          >
                            <NavLink
                              to={item.path}
                              className={({ isActive }) =>
                                `${styles.navItem} ${isActive && !isEditing ? styles.active : ""}`
                              }
                              style={isEditing ? { pointerEvents: "none" } : {}} // 링크 기능 비활성화
                            >
                              <span className={styles.navIcon}>
                                {item.icon || "🔹"}
                              </span>
                              {!isCollapsed && (
                                <span className={styles.navLabel}>
                                  {item.label}
                                </span>
                              )}
                            </NavLink>

                            {isEditing && !isCollapsed && (
                              <div
                                className={styles.editTools}
                                onClick={(e) => e.stopPropagation()}
                              >
                                <label className={styles.switch}>
                                  <input
                                    type="checkbox"
                                    checked={item.isVisible}
                                    onChange={() =>
                                      handleToggleVisible(item.id)
                                    }
                                  />
                                  <span className={styles.slider}></span>
                                </label>
                              </div>
                            )}
                          </div>
                        )}
                      </Draggable>
                    );
                  },
                )}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>
      </nav>

      {/* [섹션 3] 하단 유틸리티: 편집 버튼(고정) 및 사용자 설정 */}
      <div className={styles.sidebarBottom}>
        {isEditing && !isCollapsed && (
          <div className={styles.editActions}>
            <button className={styles.saveBtn} onClick={handleEditSave}>
              확인
            </button>
            <button
              className={styles.cancelBtn}
              onClick={() => setIsEditing(false)}
            >
              취소
            </button>
          </div>
        )}

        <div className={styles.userRow}>
          <div className={styles.userAvatar}>{user?.name?.[0]}</div>
          {!isCollapsed && (
            <span className={styles.userName}>{user?.name}</span>
          )}
        </div>
        <div className={styles.bottomButtons}>
          <button
            className={styles.bottomBtn}
            onClick={() => setShowConfig(true)}
          >
            ⚙️ {!isCollapsed && "설정"}
          </button>
          <button className={styles.bottomBtn} onClick={logout}>
            🚪 {!isCollapsed && "로그아웃"}
          </button>
        </div>
      </div>

      {showConfig && <SettingsModal onClose={() => setShowConfig(false)} />}
    </aside>
  );
};

export default Sidebar;
