import React, { useEffect, useState, useCallback, useMemo } from "react";
import * as Icon from "lucide-react";
import * as Re from "recharts";

import {
  dashboardService,
  DashboardSummary,
  SalesItem,
} from "@services/dashboardService";
import styles from "./DashboardPage.module.css";

// --- 📍 툴팁 관련 상수 및 스타일 정의 ---
const TOOLTIP_LABELS: Record<string, string> = {
  sales: "매출액",
  purchase: "매입액",
  profit: "순이익",
};

const sharedTooltipProps = {
  contentStyle: {
    backgroundColor: "var(--bg-card)",
    borderColor: "var(--border-color)",
    borderRadius: "12px",
    padding: "12px",
    boxShadow: "0 8px 24px rgba(0, 0, 0, 0.2)",
    border: "1px solid var(--border-color)",
  },
  labelStyle: {
    color: "var(--text-main)",
    fontWeight: 700,
    marginBottom: "6px",
    fontSize: "0.9rem",
  },
  itemStyle: {
    fontSize: "0.85rem",
    padding: "2px 0",
  },
};

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isItemUpdating, setIsItemUpdating] = useState(false);

  const [selectedYear, setSelectedYear] = useState<number>(2025);
  const [showAllLowStock, setShowAllLowStock] = useState(false);
  const [salesMode, setSalesMode] = useState<"top" | "bot">("top");
  const [selectedItem, setSelectedItem] = useState<SalesItem | null>(null);

  // --- 📍 데이터 페칭 로직 ---
  const fetchDashboardData = useCallback(
    async (isFirst: boolean = false) => {
      try {
        if (isFirst) setIsInitialLoading(true);
        else setIsItemUpdating(true);

        const summary = await dashboardService.getSummary(
          selectedYear,
          365,
          5,
          50,
        );
        setData(summary);

        const targetList =
          salesMode === "top" ? summary.topSales : summary.botSales;

        if (targetList && targetList.length > 0) {
          const stillExists = targetList.find(
            (item) => item.id === selectedItem?.id,
          );
          setSelectedItem(stillExists || targetList[0]);
        }
      } catch (error) {
        console.error("데이터 로드 실패:", error);
      } finally {
        setIsInitialLoading(false);
        setIsItemUpdating(false);
      }
    },
    [selectedYear, salesMode, selectedItem?.id],
  );

  useEffect(() => {
    fetchDashboardData(true);
  }, []);

  useEffect(() => {
    if (!isInitialLoading) fetchDashboardData(false);
  }, [selectedYear, salesMode]);

  const currentSalesData = useMemo(() => {
    if (!data) return [];
    return salesMode === "top" ? data.topSales : data.botSales;
  }, [data, salesMode]);

  if (isInitialLoading) {
    return (
      <div className={styles.loadingContainer}>
        <Icon.Loader2 className={styles.spinner} />
        <p>전체 경영 지표 및 {selectedYear}년 데이터를 구성 중입니다...</p>
      </div>
    );
  }

  if (!data)
    return <div className={styles.error}>데이터를 불러올 수 없습니다.</div>;

  const lowStockItems = data.lowInventory.items;
  const displayedInventory = showAllLowStock
    ? lowStockItems
    : lowStockItems.slice(0, 3);

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>재고 및 매출 통합 대시보드</h1>
          <p className={styles.subtitle}>
            시스템 가동 이후 전체 누적 실적 및 품목별 추이 정밀 분석
          </p>
        </div>
      </header>

      {/* 1. 상단: 전체 기간 실적 (메인 차트) */}
      <div className={styles.topFullSection}>
        <section className={`${styles.card} ${styles.mainGraphCard}`}>
          <div className={styles.sectionHeader}>
            <div className={styles.titleWithIcon}>
              <Icon.TrendingUp size={18} color="var(--accent-color)" />
              <h2>전체 기간 경영 실적 추이 (누적 매출/손익)</h2>
            </div>
          </div>
          <div className={styles.chartWrapper}>
            <Re.ResponsiveContainer width="100%" height={350}>
              <Re.ComposedChart data={data.monthlyStats || []}>
                <Re.CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="var(--border-color)"
                />
                <Re.XAxis
                  dataKey="month"
                  fontSize={10}
                  tick={{ fill: "var(--text-sub)" }}
                />
                <Re.YAxis
                  fontSize={10}
                  tick={{ fill: "var(--text-sub)" }}
                  tickFormatter={(val) => `₩${(val / 1000000).toFixed(0)}M`}
                />
                <Re.Tooltip
                  {...sharedTooltipProps}
                  formatter={(val: any) => `₩${Number(val).toLocaleString()}`}
                />
                <Re.Legend verticalAlign="top" height={36} />
                <Re.Bar
                  dataKey="sales"
                  name="총 매출액"
                  fill="var(--accent-color)"
                  radius={[4, 4, 0, 0]}
                  barSize={20}
                />
                <Re.Bar
                  dataKey="purchase"
                  name="총 매입액"
                  fill="var(--text-sub)"
                  opacity={0.3}
                  radius={[4, 4, 0, 0]}
                  barSize={20}
                />
                <Re.Line
                  type="monotone"
                  dataKey="profit"
                  name="운영 손익"
                  stroke="#8b5cf6"
                  strokeWidth={3}
                  dot={{ r: 4, fill: "#8b5cf6" }}
                />
              </Re.ComposedChart>
            </Re.ResponsiveContainer>
          </div>
        </section>
      </div>

      <div className={styles.bottomGrid}>
        {/* 2. 좌측: 긴급 재고 */}
        <section className={`${styles.card} ${styles.inventoryCard}`}>
          <div className={styles.sectionHeader}>
            <div className={styles.titleWithIcon}>
              <Icon.AlertTriangle size={18} color="#ff4757" />
              <h2>
                긴급 구매:{" "}
                <span className={styles.redText}>
                  {data.lowInventory.total_count}종
                </span>
              </h2>
            </div>
            {/* 📍 '더보기' 버튼을 상단 우측 헤더로 이동 */}
            {lowStockItems.length > 3 && (
              <button
                className={styles.headerMoreButton}
                onClick={() => setShowAllLowStock(!showAllLowStock)}
              >
                {showAllLowStock ? "접기" : "더보기"}
                {showAllLowStock ? (
                  <Icon.ChevronUp size={14} />
                ) : (
                  <Icon.ChevronDown size={14} />
                )}
              </button>
            )}
          </div>
          <div className={styles.inventoryListArea}>
            <ul className={styles.inventoryList}>
              {displayedInventory.map((item) => (
                <li key={item.id} className={styles.inventoryItem}>
                  <div className={styles.itemInfo}>
                    <span className={styles.partId}>{item.id}</span>
                    <span className={styles.productName}>{item.name}</span>
                  </div>
                  <div className={styles.stockStatus}>
                    <span className={styles.stockCount}>{item.stock}</span>
                    <span className={styles.stockUnit}>개</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* 3. 우측: 품목 상세 분석 및 리스트 */}
        <div
          className={`${styles.combinedSalesSection} ${
            isItemUpdating ? styles.updating : ""
          }`}
        >
          <section className={`${styles.card} ${styles.itemDetailChartCard}`}>
            <div className={styles.sectionHeader}>
              <div className={styles.titleWithIcon}>
                <Icon.Activity size={18} color="var(--accent-color)" />
                <h2>
                  품목 분석:{" "}
                  <span className={styles.highlightText}>
                    {selectedItem?.id}
                  </span>
                </h2>
              </div>
              <div className={styles.inlineFilterGroup}>
                <div className={styles.miniSelectWrapper}>
                  <select
                    className={styles.yearSelect}
                    value={selectedYear}
                    onChange={(e) => setSelectedYear(Number(e.target.value))}
                  >
                    <option value={2025}>2025년</option>
                    <option value={2024}>2024년</option>
                    <option value={2023}>2023년</option>
                  </select>
                </div>
                {isItemUpdating ? (
                  <Icon.Loader2 size={14} className={styles.miniSpinner} />
                ) : (
                  selectedItem && (
                    <div className={styles.itemBadge}>
                      운영 손익 ₩{selectedItem.amount.toLocaleString()}
                    </div>
                  )
                )}
              </div>
            </div>
            <div className={styles.miniChartWrapper}>
              <Re.ResponsiveContainer width="100%" height={200}>
                <Re.ComposedChart data={selectedItem?.monthlyTrend || []}>
                  <Re.CartesianGrid
                    strokeDasharray="2 2"
                    vertical={false}
                    stroke="var(--border-color)"
                    opacity={0.5}
                  />
                  <Re.XAxis
                    dataKey="month"
                    fontSize={9}
                    tick={{ fill: "var(--text-sub)" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Re.Tooltip
                    {...sharedTooltipProps}
                    formatter={(val: any, name?: string) => {
                      const safeName = name || "";
                      return [
                        `₩${Number(val).toLocaleString()}`,
                        TOOLTIP_LABELS[safeName] || safeName,
                      ];
                    }}
                  />
                  <Re.Area
                    type="monotone"
                    dataKey="sales"
                    name="매출액"
                    fill="var(--accent-color)"
                    fillOpacity={0.1}
                    stroke="none"
                  />
                  <Re.Bar
                    dataKey="purchase"
                    name="매입액"
                    fill="var(--text-sub)"
                    opacity={0.2}
                    barSize={12}
                  />
                  <Re.Line
                    type="monotone"
                    dataKey="profit"
                    name="순이익"
                    stroke={
                      selectedItem && selectedItem.amount >= 0
                        ? "#22c55e"
                        : "#ff4757"
                    }
                    strokeWidth={2}
                    dot={false}
                  />
                </Re.ComposedChart>
              </Re.ResponsiveContainer>
            </div>
          </section>

          <section className={`${styles.card} ${styles.tableSection}`}>
            <div className={styles.sectionHeader}>
              <div className={styles.titleWithIcon}>
                {salesMode === "top" ? (
                  <Icon.ArrowUpCircle size={18} color="#27ae60" />
                ) : (
                  <Icon.ArrowDownCircle size={18} color="#ff4757" />
                )}
                <h2>
                  {selectedYear}년 성과 {salesMode === "top" ? "상위" : "하위"}{" "}
                  품목
                </h2>
              </div>
              <div className={styles.toggleGroup}>
                <button
                  className={`${styles.toggleBtn} ${
                    salesMode === "top" ? styles.active : ""
                  }`}
                  onClick={() => setSalesMode("top")}
                >
                  상위
                </button>
                <button
                  className={`${styles.toggleBtn} ${
                    salesMode === "bot" ? styles.active : ""
                  }`}
                  onClick={() => setSalesMode("bot")}
                >
                  하위
                </button>
              </div>
            </div>
            <div className={styles.tableWrapper}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>품목 번호</th>
                    <th className={styles.textRight}>누적 매출액</th>
                    <th className={styles.textRight}>운영 손익</th>
                  </tr>
                </thead>
                <tbody>
                  {currentSalesData.map((item: SalesItem) => (
                    <tr
                      key={`${selectedYear}-${item.id}`}
                      className={`${styles.clickableRow} ${
                        selectedItem?.id === item.id ? styles.selectedRow : ""
                      }`}
                      onClick={() => setSelectedItem(item)}
                    >
                      <td className={styles.bold}>{item.id}</td>
                      <td className={`${styles.textRight} ${styles.blueText}`}>
                        ₩{item.sales.toLocaleString()}
                      </td>
                      <td
                        className={`${styles.textRight} ${
                          item.amount < 0 ? styles.redText : styles.blueText
                        } ${styles.bold}`}
                      >
                        {item.amount < 0 ? "▼" : "▲"} ₩
                        {Math.abs(item.amount).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
