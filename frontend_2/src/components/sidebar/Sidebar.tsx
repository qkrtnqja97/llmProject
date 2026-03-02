import React, { useState, useMemo } from "react";
import { Link, useLocation } from "react-router-dom";
import styles from "./Sidebar.module.css";
import { useAuth } from "@context/AuthContext";
import logoImg from "@assets/logo_1.png";
import nameImg from "@assets/name_1.png";
import * as LucideIcons from "lucide-react";
import { PATHS } from "@routes/paths";

interface MenuItem {
  id: string;
  label: string;
  icon: string;
  path?: string;
  isVisible: boolean;
  parentId: string | null;
  isGroup?: boolean;
  children: MenuItem[];
}

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
  onOpenSettings: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  isCollapsed,
  onToggle,
  onOpenSettings,
}) => {
  const location = useLocation();
  const { user, logout, userSettings } = useAuth();

  const [openMenus, setOpenMenus] = useState<Record<string, boolean>>({
    "group-work": true,
    "group-sales": true,
    "group-manage": true,
  });

  const toggleGroup = (id: string) => {
    if (isCollapsed) return;
    setOpenMenus((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const menuTree = useMemo(() => {
    const userRole = userSettings?.role || "user";
    const userTeam = userSettings?.team || "general";

    // 1. 시스템에 정의된 기본 메뉴 (기능 추가 시 여기를 먼저 수정)
    const baseMenus: any[] = [
      {
        id: "ai-search",
        label: "AI 업무검색",
        path: PATHS.AI_SEARCH,
        isVisible: true,
        icon: "Search",
        parentId: null,
      },
      {
        id: "dashboard",
        label: "대시보드",
        path: PATHS.DASHBOARD,
        isVisible: true,
        icon: "LayoutDashboard",
        parentId: null,
      },
      {
        id: "group-work",
        label: "업무 관리",
        isVisible: true,
        icon: "Briefcase",
        parentId: null,
        isGroup: true,
      },
      {
        id: "work-create",
        label: "업무 작성",
        path: PATHS.WORK.CREATE,
        isVisible: true,
        icon: "PenLine",
        parentId: "group-work",
      },
      {
        id: "work-log",
        label: "일지 작성",
        path: PATHS.WORK.LOG,
        isVisible: true,
        icon: "FileText",
        parentId: "group-work",
      },
    ];

    if (userRole === "admin" || userTeam === "hr") {
      baseMenus.push(
        {
          id: "group-hr",
          label: "인사/행정",
          isVisible: true,
          icon: "Users2",
          parentId: null,
          isGroup: true,
        },
        {
          id: "hr-emp",
          label: "사원 관리",
          path: PATHS.HR.EMPLOYEES,
          isVisible: true,
          icon: "UserCog",
          parentId: "group-hr",
        },
        {
          id: "hr-att",
          label: "근태 기록",
          path: PATHS.HR.ATTENDANCE,
          isVisible: true,
          icon: "CalendarCheck",
          parentId: "group-hr",
        },
      );
    }

    if (userRole === "admin" || userTeam === "finance") {
      baseMenus.push(
        {
          id: "group-finance",
          label: "회계/재무",
          isVisible: true,
          icon: "Landmark",
          parentId: null,
          isGroup: true,
        },
        {
          id: "finance-voucher",
          label: "전표 관리",
          path: PATHS.FINANCE.VOUCHER,
          isVisible: true,
          icon: "ReceiptText",
          parentId: "group-finance",
        },
        {
          id: "finance-settlement",
          label: "결산 보고",
          path: PATHS.FINANCE.SETTLEMENT,
          isVisible: true,
          icon: "BarChart3",
          parentId: "group-finance",
        },
      );
    }

    if (userRole === "admin" || userTeam === "sales") {
      baseMenus.push(
        {
          id: "group-sales",
          label: "영업/판매",
          isVisible: true,
          icon: "BadgeDollarSign",
          parentId: null,
          isGroup: true,
        },
        {
          id: "sales-quote",
          label: "견적 관리",
          path: PATHS.SALES.QUOTE,
          isVisible: true,
          icon: "Quote",
          parentId: "group-sales",
        },
        {
          id: "sales-order",
          label: "수주 관리",
          path: PATHS.SALES.ORDER_SO,
          isVisible: true,
          icon: "FileSpreadsheet",
          parentId: "group-sales",
        },
      );
    }

    if (
      userRole === "admin" ||
      ["purchase", "logistics", "product"].includes(userTeam)
    ) {
      baseMenus.push(
        {
          id: "group-manage",
          label: "운영 관리",
          isVisible: true,
          icon: "Settings2",
          parentId: null,
          isGroup: true,
        },
        {
          id: "manage-inventory",
          label: "재고 관리",
          path: PATHS.MANAGE.INVENTORY,
          isVisible: true,
          icon: "Box",
          parentId: "group-manage",
        },
        {
          id: "manage-order",
          label: "발주 관리",
          path: PATHS.MANAGE.ORDER,
          isVisible: true,
          icon: "ShoppingCart",
          parentId: "group-manage",
        },
        {
          id: "manage-product",
          label: "제품 관리",
          path: PATHS.MANAGE.PRODUCT,
          isVisible: true,
          icon: "Package",
          parentId: "group-manage",
        },
      );
    }

    baseMenus.push(
      {
        id: "contact",
        label: "연락처",
        path: PATHS.CONTACT,
        isVisible: true,
        icon: "Contact2",
        parentId: null,
      },
      {
        id: "history",
        label: "검색 기록",
        path: PATHS.HISTORY,
        isVisible: true,
        icon: "History",
        parentId: null,
      },
    );

    // 2. 서버/사용자 설정 데이터 파싱
    const rawData = userSettings?.sidebarMenus || userSettings?.menu_config;
    let configMenus: any[] = [];
    if (rawData) {
      try {
        configMenus =
          typeof rawData === "string" ? JSON.parse(rawData) : rawData;
      } catch (e) {
        console.error("Sidebar menu parsing error:", e);
      }
    }

    // 3. 📍 메뉴 병합 로직: 새 기능이 설정 데이터에 없을 경우를 대비하여 병합
    let finalMenus = baseMenus;
    if (configMenus && configMenus.length > 0) {
      // 설정 데이터에 있는 ID 목록
      const configIds = configMenus.map((m) => m.id);
      // 설정에 없는 '신규 메뉴'만 추출하여 합침
      const newMenus = baseMenus.filter((m) => !configIds.includes(m.id));
      finalMenus = [...configMenus, ...newMenus];
    }

    const menuMap = new Map<string, MenuItem>();
    const visibleMenus = finalMenus.filter((m: any) => m.isVisible !== false);

    visibleMenus.forEach((m) => {
      menuMap.set(m.id, {
        ...m,
        children: [],
        icon: m.icon || "Grid",
        path: m.path || (m.id.startsWith("/") ? m.id : `/${m.id}`),
      });
    });

    const tree: MenuItem[] = [];
    visibleMenus.forEach((m) => {
      const item = menuMap.get(m.id);
      if (!item) return;
      if (m.parentId && menuMap.has(m.parentId)) {
        menuMap.get(m.parentId)!.children.push(item);
      } else {
        tree.push(item);
      }
    });

    return tree;
  }, [userSettings, user]);

  const renderIcon = (name: string, size: number) => {
    const IconComponent = (LucideIcons as any)[name] || LucideIcons.Grid;
    return <IconComponent size={size} />;
  };

  const checkActive = (path: string | undefined) => {
    if (!path) return false;
    return location.pathname === path;
  };

  const isChildActive = (node: MenuItem) => {
    return node.children.some((child) => checkActive(child.path));
  };

  return (
    <aside
      className={`${styles.sidebar} ${isCollapsed ? styles.collapsed : ""}`}
    >
      <div className={styles.header}>
        <Link
          to={userSettings?.startPage || PATHS.DASHBOARD}
          className={styles.logoLink}
        >
          <div className={styles.logoIcon}>
            <img src={logoImg} alt="Logo" className={styles.sidebarLogoImg} />
          </div>
          {!isCollapsed && (
            <div className={styles.logoNameWrapper}>
              <img src={nameImg} alt="Name" className={styles.logoNameImg} />
            </div>
          )}
        </Link>
        <button className={styles.toggleBtn} onClick={onToggle}>
          {isCollapsed ? (
            <LucideIcons.ChevronRight size={16} />
          ) : (
            <LucideIcons.ChevronLeft size={16} />
          )}
        </button>
      </div>

      <nav className={styles.nav}>
        {menuTree.map((node: MenuItem) => {
          const isGroupMenu = node.isGroup || node.children.length > 0;
          const isActive = checkActive(node.path);
          const hasActiveChild = isChildActive(node);

          if (isGroupMenu) {
            const isOpen = openMenus[node.id] ?? false;
            return (
              <div key={node.id} className={styles.group}>
                <div
                  className={`${styles.groupLabel} ${hasActiveChild ? styles.parentActive : ""} ${isActive ? styles.active : ""}`}
                  onClick={() => toggleGroup(node.id)}
                >
                  <div className={styles.labelLeft}>
                    <span className={styles.icon}>
                      {renderIcon(node.icon, 18)}
                    </span>
                    {!isCollapsed && <span>{node.label}</span>}
                  </div>
                  {!isCollapsed &&
                    (isOpen ? (
                      <LucideIcons.ChevronUp size={14} />
                    ) : (
                      <LucideIcons.ChevronDown size={14} />
                    ))}
                </div>
                {!isCollapsed && isOpen && (
                  <div className={styles.subMenu}>
                    {node.children.map((child) => (
                      <Link
                        key={child.id}
                        to={child.path!}
                        className={`${styles.subMenuItem} ${checkActive(child.path) ? styles.active : ""}`}
                      >
                        <span className={styles.icon}>
                          {renderIcon(child.icon, 16)}
                        </span>
                        <span>{child.label}</span>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            );
          }

          return (
            <Link
              key={node.id}
              to={node.path!}
              className={`${styles.menuItem} ${isActive ? styles.active : ""}`}
              title={node.label}
            >
              <span className={styles.icon}>{renderIcon(node.icon, 18)}</span>
              {!isCollapsed && <span>{node.label}</span>}
            </Link>
          );
        })}
      </nav>

      <div className={styles.footer}>
        {!isCollapsed && (
          <div className={styles.userInfo}>
            <div className={styles.userAvatar}>
              <LucideIcons.User size={18} />
            </div>
            <div className={styles.userText}>
              <span className={styles.userName}>
                {(userSettings as any)?.name || user || "사용자"}
              </span>
              <span className={styles.userRole}>
                {userSettings?.team || "일반"}
              </span>
            </div>
          </div>
        )}
        <div className={styles.footerActions}>
          <button
            className={styles.footerActionBtn}
            onClick={onOpenSettings}
            title="설정"
          >
            <LucideIcons.Settings size={18} />
            {!isCollapsed && <span>설정</span>}
          </button>
          <button
            className={`${styles.footerActionBtn} ${styles.logout}`}
            onClick={logout}
            title="로그아웃"
          >
            <LucideIcons.LogOut size={18} />
            {!isCollapsed && <span>로그아웃</span>}
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
