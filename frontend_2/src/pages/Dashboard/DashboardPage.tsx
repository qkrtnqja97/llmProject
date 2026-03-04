import React, {
  useEffect,
  useState,
  useCallback,
  useMemo,
  useRef,
} from "react";
import * as Icon from "lucide-react";
import * as Re from "recharts";

import {
  dashboardService,
  DashboardSummary,
  SalesItem,
} from "@services/dashboardService";
import styles from "./DashboardPage.module.css";

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

  // 연도 상태 분리
  const [graphYear, setGraphYear] = useState<number>(2025);
  const [tableYear, setTableYear] = useState<number>(2025);

  // 그래프 지표 가시성 상태
  const [visibleMetrics, setVisibleMetrics] = useState({
    sales: true,
    purchase: true,
    profit: true,
  });

  // 📍 긴급 구매 확장 상태
  const [isInventoryExpanded, setIsInventoryExpanded] = useState(false);

  const [salesMode, setSalesMode] = useState<"top" | "bot">("top");
  const [selectedItem, setSelectedItem] = useState<SalesItem | null>(null);

  const [isGraphYearOpen, setIsGraphYearOpen] = useState(false);
  const [isTableYearOpen, setIsTableYearOpen] = useState(false);
  const graphDropdownRef = useRef<HTMLDivElement>(null);
  const tableDropdownRef = useRef<HTMLDivElement>(null);

  // 외부 클릭 시 드롭다운 닫기
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      if (
        graphDropdownRef.current &&
        !graphDropdownRef.current.contains(target)
      )
        setIsGraphYearOpen(false);
      if (
        tableDropdownRef.current &&
        !tableDropdownRef.current.contains(target)
      )
        setIsTableYearOpen(false);
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const fetchDashboardData = useCallback(
    async (isFirst: boolean = false) => {
      try {
        if (isFirst) setIsInitialLoading(true);
        else setIsItemUpdating(true);

        const summary = await dashboardService.getSummary(
          tableYear,
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
    [tableYear, salesMode, selectedItem?.id],
  );

  useEffect(() => {
    fetchDashboardData(true);
  }, []);

  useEffect(() => {
    if (!isInitialLoading) fetchDashboardData(false);
  }, [tableYear, salesMode]);

  const filteredMonthlyStats = useMemo(() => {
    if (!data || !data.monthlyStats) return [];
    return data.monthlyStats.filter((stat) =>
      stat.month.startsWith(graphYear.toString()),
    );
  }, [data, graphYear]);

  const currentSalesData = useMemo(() => {
    if (!data) return [];
    return salesMode === "top" ? data.topSales : data.botSales;
  }, [data, salesMode]);

  const toggleMetric = (metric: keyof typeof visibleMetrics) => {
    setVisibleMetrics((prev) => ({ ...prev, [metric]: !prev[metric] }));
  };

  if (isInitialLoading) {
    return (
      <div className={styles.loadingContainer}>
        <Icon.Loader2 className={styles.spinner} />
        <p>경영 지표 데이터를 구성 중입니다...</p>
      </div>
    );
  }

  if (!data)
    return <div className={styles.error}>데이터를 불러올 수 없습니다.</div>;

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>재고 및 매출 통합 대시보드</h1>
          <p className={styles.subtitle}>
            부문별 독립적 기간 설정 및 커스텀 지표 분석
          </p>
        </div>
      </header>

      <div className={styles.topGrid}>
        {/* --- 경영 실적 섹션 --- */}
        <section className={`${styles.card} ${styles.mainGraphCard}`}>
          <div className={styles.sectionHeader}>
            <div className={styles.titleWithIcon}>
              <Icon.TrendingUp size={18} color="var(--accent-color)" />
              <h2>{graphYear}년 경영 실적 추이</h2>
            </div>

            <div className={styles.headerControls}>
              <div className={styles.metricFilters}>
                <label className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    checked={visibleMetrics.sales}
                    onChange={() => toggleMetric("sales")}
                  />
                  <span
                    className={styles.customCheck}
                    style={{ backgroundColor: "var(--accent-color)" }}
                  ></span>
                  매출
                </label>
                <label className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    checked={visibleMetrics.purchase}
                    onChange={() => toggleMetric("purchase")}
                  />
                  <span
                    className={styles.customCheck}
                    style={{ backgroundColor: "var(--text-sub)" }}
                  ></span>
                  매입
                </label>
                <label className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    checked={visibleMetrics.profit}
                    onChange={() => toggleMetric("profit")}
                  />
                  <span
                    className={styles.customCheck}
                    style={{ backgroundColor: "#22c55e" }}
                  ></span>
                  손익
                </label>
              </div>

              <div
                className={styles.customSelectContainer}
                ref={graphDropdownRef}
              >
                <div
                  className={styles.customSelectTrigger}
                  onClick={() => setIsGraphYearOpen(!isGraphYearOpen)}
                >
                  <span>{graphYear}년</span>
                  <Icon.ChevronDown
                    size={14}
                    className={isGraphYearOpen ? styles.rotate : ""}
                  />
                </div>
                {isGraphYearOpen && (
                  <ul className={styles.customOptions}>
                    {[2025, 2024, 2023].map((year) => (
                      <li
                        key={year}
                        onClick={() => {
                          setGraphYear(year);
                          setIsGraphYearOpen(false);
                        }}
                      >
                        {year}년
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>

          {/* 📍 CSS의 .chartArea 스타일이 적용되는 지점 */}
          <div className={styles.chartArea}>
            <Re.ResponsiveContainer width="100%" height="100%">
              <Re.ComposedChart data={filteredMonthlyStats}>
                <Re.CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="var(--border-color)"
                />
                <Re.XAxis
                  dataKey="month"
                  fontSize={10}
                  tickFormatter={(val) => val.split("-")[1] + "월"}
                />
                <Re.YAxis
                  yAxisId="left"
                  fontSize={10}
                  tickFormatter={(val) => `₩${(val / 1000000).toFixed(0)}M`}
                />
                <Re.YAxis
                  yAxisId="right"
                  orientation="right"
                  fontSize={10}
                  tickFormatter={(val) => `₩${(val / 1000000).toFixed(0)}M`}
                  stroke="#22c55e"
                />
                <Re.Tooltip
                  {...sharedTooltipProps}
                  formatter={(val: any) => `₩${Number(val).toLocaleString()}`}
                />

                {visibleMetrics.sales && (
                  <Re.Bar
                    yAxisId="left"
                    dataKey="sales"
                    name="총 매출액"
                    fill="var(--accent-color)"
                    radius={[4, 4, 0, 0]}
                    barSize={20}
                  />
                )}
                {visibleMetrics.purchase && (
                  <Re.Bar
                    yAxisId="left"
                    dataKey="purchase"
                    name="총 매입액"
                    fill="var(--text-sub)"
                    radius={[4, 4, 0, 0]}
                    barSize={20}
                    style={{ opacity: 0.3 }}
                  />
                )}
                {visibleMetrics.profit && (
                  <Re.Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="profit"
                    name="운영 손익"
                    stroke="#22c55e"
                    strokeWidth={3}
                    dot={{ r: 4, fill: "#22c55e" }}
                  />
                )}
              </Re.ComposedChart>
            </Re.ResponsiveContainer>
          </div>
        </section>

        {/* --- 📍 긴급 구매 섹션 (수정됨) --- */}
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
            {/* 📍 더보기/접기 버튼 추가 */}
            <button
              className={styles.headerMoreButton}
              onClick={() => setIsInventoryExpanded(!isInventoryExpanded)}
            >
              {isInventoryExpanded ? "접기" : "더보기"}
              {isInventoryExpanded ? (
                <Icon.ChevronUp size={14} />
              ) : (
                <Icon.ChevronDown size={14} />
              )}
            </button>
          </div>

          {/* 📍 expanded 클래스 조건부 부여 */}
          <div
            className={`${styles.inventoryListArea} ${isInventoryExpanded ? styles.expanded : ""}`}
          >
            <ul className={styles.inventoryList}>
              {(isInventoryExpanded
                ? data.lowInventory.items
                : data.lowInventory.items.slice(0, 3)
              ).map((item) => (
                <li key={item.id} className={styles.inventoryItem}>
                  <div className={styles.itemInfo}>
                    <span className={styles.partId}>{item.id}</span>
                    <span className={styles.productName}>{item.name}</span>
                  </div>
                  <div className={styles.stockStatus}>
                    <span className={styles.stockCount}>{item.stock}</span>개
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </div>

      <div className={styles.bottomGrid}>
        <div
          className={`${styles.combinedSalesSection} ${isItemUpdating ? styles.updating : ""}`}
        >
          <section className={`${styles.card} ${styles.tableSection}`}>
            <div className={styles.sectionHeader}>
              <div className={styles.titleWithIcon}>
                {salesMode === "top" ? (
                  <Icon.ArrowUpCircle size={18} color="#27ae60" />
                ) : (
                  <Icon.ArrowDownCircle size={18} color="#ff4757" />
                )}
                <h2>{tableYear}년 성과 품목</h2>
              </div>
              <div className={styles.inlineFilterGroup}>
                <div
                  className={styles.customSelectContainer}
                  ref={tableDropdownRef}
                >
                  <div
                    className={styles.customSelectTrigger}
                    onClick={() => setIsTableYearOpen(!isTableYearOpen)}
                  >
                    <span>{tableYear}년</span>
                    <Icon.ChevronDown
                      size={14}
                      className={isTableYearOpen ? styles.rotate : ""}
                    />
                  </div>
                  {isTableYearOpen && (
                    <ul className={styles.customOptions}>
                      {[2025, 2024, 2023].map((year) => (
                        <li
                          key={year}
                          onClick={() => {
                            setTableYear(year);
                            setIsTableYearOpen(false);
                          }}
                        >
                          {year}년
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
                <div className={styles.toggleGroup}>
                  <button
                    className={`${styles.toggleBtn} ${salesMode === "top" ? styles.active : ""}`}
                    onClick={() => setSalesMode("top")}
                  >
                    상위
                  </button>
                  <button
                    className={`${styles.toggleBtn} ${salesMode === "bot" ? styles.active : ""}`}
                    onClick={() => setSalesMode("bot")}
                  >
                    하위
                  </button>
                </div>
              </div>
            </div>
            <div className={styles.tableWrapper}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>품목 번호</th>
                    <th className={styles.textRight}>누적 매출액</th>
                    <th className={styles.textRight}>누적 매입액</th>
                    <th className={styles.textRight}>운영 손익</th>
                  </tr>
                </thead>
                <tbody>
                  {currentSalesData.map((item: SalesItem) => (
                    <tr
                      key={`${tableYear}-${item.id}`}
                      className={`${styles.clickableRow} ${selectedItem?.id === item.id ? styles.selectedRow : ""}`}
                      onClick={() => setSelectedItem(item)}
                    >
                      <td className={styles.bold}>{item.id}</td>
                      <td className={`${styles.textRight} ${styles.blueText}`}>
                        ₩{item.sales.toLocaleString()}
                      </td>
                      <td className={`${styles.textRight} ${styles.subText}`}>
                        ₩{item.purchase.toLocaleString()}
                      </td>
                      <td
                        className={`${styles.textRight} ${styles.bold}`}
                        style={{
                          color: item.amount >= 0 ? "#22c55e" : "#ef4444",
                        }}
                      >
                        {item.amount >= 0 ? "▲" : "▼"} ₩
                        {Math.abs(item.amount).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

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
                    axisLine={false}
                    tickLine={false}
                  />
                  <Re.Tooltip
                    {...sharedTooltipProps}
                    formatter={(val: any, name?: string) => [
                      `₩${Number(val).toLocaleString()}`,
                      TOOLTIP_LABELS[name || ""] || name,
                    ]}
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
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
