/* src/components/modals/SettingsModal.tsx */
import React, { useState, useEffect, useMemo } from "react";
import * as LucideIcons from "lucide-react";
import * as DndCore from "@dnd-kit/core";
import * as DndSortable from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { useAuth } from "@context/AuthContext";
import { userService } from "@services/userService";
import { PATHS } from "@routes/paths";
import styles from "./SettingsModal.module.css";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  theme: string;
  setTheme: (theme: string) => void;
}

interface RawMenuItem {
  id: string;
  label: string;
  icon: string;
  isVisible: boolean;
  parentId: string | null;
  isGroup?: boolean;
  path?: string;
}

// 📍 [시스템 전체 기본 메뉴 정의]
const DEFAULT_TOTAL_MENUS: RawMenuItem[] = [
  {
    id: "ai-search",
    label: "AI 업무검색",
    icon: "Search",
    isVisible: true,
    parentId: null,
    path: PATHS.AI_SEARCH,
  },
  {
    id: "dashboard",
    label: "대시보드",
    icon: "LayoutDashboard",
    isVisible: true,
    parentId: null,
    path: PATHS.DASHBOARD,
  },

  // 인사/행정 그룹
  {
    id: "group-hr",
    label: "인사/행정",
    icon: "Users2",
    isVisible: true,
    parentId: null,
    isGroup: true,
  },
  {
    id: "hr-emp",
    label: "사원 관리",
    icon: "UserCog",
    isVisible: true,
    parentId: "group-hr",
    path: PATHS.HR.EMPLOYEES,
  },
  {
    id: "hr-att",
    label: "근태 기록",
    icon: "CalendarCheck",
    isVisible: true,
    parentId: "group-hr",
    path: PATHS.HR.ATTENDANCE,
  },

  // 회계/재무 그룹
  {
    id: "group-finance",
    label: "회계/재무",
    icon: "Landmark",
    isVisible: true,
    parentId: null,
    isGroup: true,
  },
  {
    id: "finance-voucher",
    label: "전표 관리",
    icon: "ReceiptText",
    isVisible: true,
    parentId: "group-finance",
    path: PATHS.FINANCE.VOUCHER,
  },
  {
    id: "finance-settlement",
    label: "결산 보고",
    icon: "BarChart3",
    isVisible: true,
    parentId: "group-finance",
    path: PATHS.FINANCE.SETTLEMENT,
  },

  // 영업/판매 그룹
  {
    id: "group-sales",
    label: "영업/판매",
    icon: "BadgeDollarSign",
    isVisible: true,
    parentId: null,
    isGroup: true,
  },
  {
    id: "sales-quote",
    label: "견적 관리",
    icon: "Quote",
    isVisible: true,
    parentId: "group-sales",
    path: PATHS.SALES.QUOTE,
  },
  {
    id: "sales-order",
    label: "수주 관리",
    icon: "FileSpreadsheet",
    isVisible: true,
    parentId: "group-sales",
    path: PATHS.SALES.ORDER_SO,
  },

  // 업무 관리 그룹
  {
    id: "group-work",
    label: "업무 관리",
    icon: "Briefcase",
    isVisible: true,
    parentId: null,
    isGroup: true,
  },
  {
    id: "work-create",
    label: "업무 작성",
    icon: "PenLine",
    isVisible: true,
    parentId: "group-work",
    path: PATHS.WORK.CREATE,
  },
  {
    id: "work-log",
    label: "일지 작성",
    icon: "FileText",
    isVisible: true,
    parentId: "group-work",
    path: PATHS.WORK.LOG,
  },

  // 운영 관리 그룹 (ERP)
  {
    id: "group-manage",
    label: "운영 관리",
    icon: "Settings2",
    isVisible: true,
    parentId: null,
    isGroup: true,
  },
  {
    id: "manage-inventory",
    label: "재고 관리",
    icon: "Box",
    isVisible: true,
    parentId: "group-manage",
    path: PATHS.MANAGE.INVENTORY,
  },
  {
    id: "manage-order",
    label: "발주 관리",
    icon: "ShoppingCart",
    isVisible: true,
    parentId: "group-manage",
    path: PATHS.MANAGE.ORDER,
  },
  {
    id: "manage-product",
    label: "제품 관리",
    icon: "Package",
    isVisible: true,
    parentId: "group-manage",
    path: PATHS.MANAGE.PRODUCT,
  },

  // 공통
  {
    id: "contact",
    label: "연락처",
    icon: "Contact2",
    isVisible: true,
    parentId: null,
    path: PATHS.CONTACT,
  },
  {
    id: "history",
    label: "검색 기록",
    icon: "History",
    isVisible: true,
    parentId: null,
    path: PATHS.HISTORY,
  },
];

const SortableItem = ({
  item,
  toggleVisibility,
  expanded,
  onToggleExpand,
}: any) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = DndSortable.useSortable({ id: item.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    zIndex: isDragging ? 2001 : "auto",
    opacity: isDragging ? 0.3 : 1,
  };

  const IconComponent = (LucideIcons as any)[item.icon] || LucideIcons.Menu;
  const isGroup =
    item.isGroup ||
    (!item.parentId && DEFAULT_TOTAL_MENUS.some((m) => m.parentId === item.id));

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`${styles.menuItem} ${item.parentId ? styles.childItem : styles.parentItem} ${isDragging ? styles.dragging : ""}`}
      {...attributes}
      {...listeners}
    >
      <div className={styles.menuLeft}>
        <LucideIcons.GripVertical size={16} className={styles.gripIcon} />
        {isGroup && (
          <button
            className={styles.expandBtn}
            onPointerDown={(e) => e.stopPropagation()}
            onClick={() => onToggleExpand(item.id)}
          >
            {expanded ? (
              <LucideIcons.ChevronDown size={14} />
            ) : (
              <LucideIcons.ChevronRight size={14} />
            )}
          </button>
        )}
        <div className={styles.menuIconText}>
          <IconComponent size={item.parentId ? 16 : 18} />
        </div>
        <span className={styles.menuLabelText}>
          {item.parentId && <span className={styles.childIndicator}>└ </span>}
          {item.label}
        </span>
      </div>
      <div
        className={styles.switchContainer}
        onPointerDown={(e) => e.stopPropagation()}
      >
        <label className={styles.customSwitch}>
          <input
            type="checkbox"
            checked={item.isVisible}
            onChange={() => toggleVisibility(item.id)}
          />
          <span className={styles.slider}></span>
        </label>
      </div>
    </div>
  );
};

const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  theme,
  setTheme,
}) => {
  const { userSettings, updateLocalSettings } = useAuth();
  const [activeTab, setActiveTab] = useState<"system" | "sidebar">("system");
  const [startPage, setStartPage] = useState(PATHS.AI_SEARCH);
  const [menus, setMenus] = useState<RawMenuItem[]>([]);
  const [expandedMenus, setExpandedMenus] = useState<string[]>([]);

  useEffect(() => {
    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    if (isOpen) {
      window.addEventListener("keydown", handleEsc);
    }

    return () => {
      window.removeEventListener("keydown", handleEsc);
    };
  }, [isOpen, onClose]);

  const sensors = DndCore.useSensors(
    DndCore.useSensor(DndCore.PointerSensor, {
      activationConstraint: { distance: 5 },
    }),
  );

  // 📍 [수정] 부서 및 권한에 따른 "시작 페이지 옵션" 필터링 로직
  const pageOptions = useMemo(() => {
    const role = userSettings?.role || "user";
    const team = userSettings?.team || "general";

    return DEFAULT_TOTAL_MENUS.filter((m) => {
      if (m.isGroup) return false; // 그룹은 시작페이지 불가

      // 부서별 권한 필터링 (Sidebar와 동일)
      if (m.id.startsWith("hr-") && role !== "admin" && team !== "hr")
        return false;
      if (m.id.startsWith("finance-") && role !== "admin" && team !== "finance")
        return false;
      if (m.id.startsWith("sales-") && role !== "admin" && team !== "sales")
        return false;
      if (
        m.id.startsWith("manage-") &&
        role !== "admin" &&
        !["purchase", "logistics", "product"].includes(team)
      )
        return false;

      return true;
    }).map((m) => ({
      id: m.path || (m.id.startsWith("/") ? m.id : `/${m.id}`),
      label: m.label,
      icon: m.icon,
    }));
  }, [userSettings]);

  // 📍 [수정] 모달 로드 시 사용자의 팀 권한에 맞는 메뉴만 초기화
  useEffect(() => {
    if (userSettings && isOpen) {
      setTheme(userSettings.theme || "navy");
      setStartPage(userSettings.startPage || PATHS.AI_SEARCH);

      const role = userSettings.role || "user";
      const team = userSettings.team || "general";

      // 현재 사용자가 수정할 수 있는 권한이 있는 메뉴만 선별
      const authorizedDefaultMenus = DEFAULT_TOTAL_MENUS.filter((m) => {
        if (m.id.startsWith("group-hr") || m.id.startsWith("hr-"))
          return role === "admin" || team === "hr";
        if (m.id.startsWith("group-finance") || m.id.startsWith("finance-"))
          return role === "admin" || team === "finance";
        if (m.id.startsWith("group-sales") || m.id.startsWith("sales-"))
          return role === "admin" || team === "sales";
        if (m.id.startsWith("group-manage") || m.id.startsWith("manage-")) {
          return (
            role === "admin" ||
            ["purchase", "logistics", "product"].includes(team)
          );
        }
        return true;
      });

      const savedMenus = userSettings.sidebarMenus || [];
      const merged = authorizedDefaultMenus.map((defaultItem) => {
        const savedItem = savedMenus.find((m: any) => m.id === defaultItem.id);
        return savedItem ? { ...defaultItem, ...savedItem } : defaultItem;
      });

      setMenus(merged);
    }
  }, [userSettings, isOpen, setTheme]);

  const handleThemeChange = (newTheme: string) => {
    setTheme(newTheme);
    updateLocalSettings({ ...userSettings, theme: newTheme });
  };

  const toggleExpand = (id: string) => {
    setExpandedMenus((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id],
    );
  };

  const handleDragEnd = (event: DndCore.DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    setMenus((prev) => {
      const oldIndex = prev.findIndex((m) => m.id === active.id);
      const newIndex = prev.findIndex((m) => m.id === over.id);
      const newOrder = DndSortable.arrayMove(prev, oldIndex, newIndex);

      const finalOrder: RawMenuItem[] = [];
      newOrder
        .filter((m) => !m.parentId)
        .forEach((p) => {
          finalOrder.push(p);
          finalOrder.push(...newOrder.filter((c) => c.parentId === p.id));
        });
      return finalOrder;
    });
  };

  const toggleVisibility = (id: string) => {
    setMenus((prev) =>
      prev.map((m) => (m.id === id ? { ...m, isVisible: !m.isVisible } : m)),
    );
  };

  const handleSave = async () => {
    try {
      const payload = { theme, startPage, sidebarMenus: menus };
      await userService.updateSettings(payload);
      updateLocalSettings(payload);
      alert("설정이 저장되었습니다.");
      onClose();
    } catch (error) {
      alert("저장 실패");
    }
  };

  if (!isOpen) return null;

  const visibleDisplayMenus = menus.filter(
    (m) => !m.parentId || expandedMenus.includes(m.parentId),
  );

  return (
    <div className={styles.overlay}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <header className={styles.header}>
          <h2>⚙️ 환경 설정</h2>
          <button className={styles.closeBtn} onClick={onClose}>
            <LucideIcons.X size={24} />
          </button>
        </header>

        <div className={styles.container}>
          <aside className={styles.tabSidebar}>
            <button
              className={`${styles.tabBtn} ${activeTab === "system" ? styles.activeTab : ""}`}
              onClick={() => setActiveTab("system")}
            >
              <LucideIcons.Settings size={18} /> 시스템 설정
            </button>
            <button
              className={`${styles.tabBtn} ${activeTab === "sidebar" ? styles.activeTab : ""}`}
              onClick={() => setActiveTab("sidebar")}
            >
              <LucideIcons.Layout size={18} /> 사이드바 구성
            </button>
          </aside>

          <main className={styles.tabContent}>
            {activeTab === "system" ? (
              <div className={styles.tabPane}>
                <div className={styles.categoryTitle}>System Settings</div>
                <section className={styles.section}>
                  <h3>
                    <LucideIcons.Palette size={18} /> 테마 설정
                  </h3>
                  <div className={styles.themeOptions}>
                    {[
                      { id: "navy", label: "심해 모드", icon: "Waves" },
                      { id: "gray", label: "그레이 모드", icon: "Monitor" },
                      { id: "sand", label: "샌드 모드", icon: "Sun" },
                    ].map((t) => (
                      <button
                        key={t.id}
                        className={`${styles.themeCard} ${theme === t.id ? styles.active : ""}`}
                        onClick={() => handleThemeChange(t.id)}
                      >
                        {React.createElement((LucideIcons as any)[t.icon], {
                          size: 24,
                          className: styles.themeIcon,
                        })}
                        <span>{t.label}</span>
                      </button>
                    ))}
                  </div>
                </section>
                <section className={styles.section}>
                  <h3>
                    <LucideIcons.Home size={18} /> 시작 페이지
                  </h3>
                  <div className={styles.pageGrid}>
                    {pageOptions.map((opt) => {
                      const Icon =
                        (LucideIcons as any)[opt.icon] || LucideIcons.Circle;
                      return (
                        <div
                          key={opt.id}
                          className={`${styles.pageCard} ${startPage === opt.id ? styles.activePage : ""}`}
                          onClick={() => setStartPage(opt.id)}
                        >
                          <div className={styles.iconWrapper}>
                            <Icon size={20} />
                          </div>
                          <span className={styles.pageLabel}>{opt.label}</span>
                          {startPage === opt.id && (
                            <LucideIcons.CheckCircle2
                              className={styles.checkIcon}
                              size={14}
                            />
                          )}
                        </div>
                      );
                    })}
                  </div>
                </section>
              </div>
            ) : (
              <div className={styles.tabPane}>
                <div className={styles.categoryTitle}>Sidebar Navigation</div>
                <div className={styles.dragInfo}>
                  ※ 권한이 있는 메뉴만 목록에 표시됩니다.
                </div>
                <div className={styles.menuList}>
                  <DndCore.DndContext
                    sensors={sensors}
                    collisionDetection={DndCore.closestCenter}
                    onDragEnd={handleDragEnd}
                  >
                    <DndSortable.SortableContext
                      items={visibleDisplayMenus.map((m) => m.id)}
                      strategy={DndSortable.verticalListSortingStrategy}
                    >
                      {visibleDisplayMenus.map((item) => (
                        <SortableItem
                          key={item.id}
                          item={item}
                          toggleVisibility={toggleVisibility}
                          expanded={expandedMenus.includes(item.id)}
                          onToggleExpand={toggleExpand}
                        />
                      ))}
                    </DndSortable.SortableContext>
                  </DndCore.DndContext>
                </div>
              </div>
            )}
          </main>
        </div>

        <footer className={styles.footer}>
          <button className={styles.cancelBtn} onClick={onClose}>
            취소
          </button>
          <button className={styles.saveBtn} onClick={handleSave}>
            <LucideIcons.Save size={18} /> 설정 저장
          </button>
        </footer>
      </div>
    </div>
  );
};

export default SettingsModal;
