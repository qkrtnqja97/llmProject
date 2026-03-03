import React, { useState, useEffect, useCallback, useMemo } from "react";
import * as LucideIcons from "lucide-react";
import styles from "./InventoryManagePage.module.css";
import { inventoryService, InventoryItem } from "@services/inventoryService";

const InventoryManagePage = () => {
  const [allInventory, setAllInventory] = useState<InventoryItem[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  // 페이지네이션 상태
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // 1. 데이터 로드
  const fetchInventory = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await inventoryService.getCurrentInventory(
        0,
        9999,
        searchTerm,
      );
      setAllInventory(response?.items || []);
    } catch (error) {
      console.error("재고 로드 실패:", error);
      setAllInventory([]);
    } finally {
      setIsLoading(false);
    }
  }, [searchTerm]);

  useEffect(() => {
    fetchInventory();
  }, [fetchInventory]);

  // 2. 현재 페이지 데이터 계산
  const displayInventory = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    return allInventory.slice(startIndex, startIndex + pageSize);
  }, [allInventory, currentPage, pageSize]);

  const totalPages = Math.ceil(allInventory.length / pageSize);

  // 3. 핸들러
  const jumpNextTen = () =>
    setCurrentPage((prev) => Math.min(prev + 10, totalPages));
  const jumpPrevTen = () => setCurrentPage((prev) => Math.max(prev - 10, 1));
  const goToFirst = () => setCurrentPage(1);
  const goToLast = () => setCurrentPage(totalPages);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  const handlePageSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setPageSize(Number(e.target.value));
    setCurrentPage(1);
  };

  const getPageNumbers = () => {
    const pageLimit = 5;
    let start = Math.max(1, currentPage - Math.floor(pageLimit / 2));
    let end = Math.min(totalPages, start + pageLimit - 1);
    if (end - start + 1 < pageLimit) {
      start = Math.max(1, end - pageLimit + 1);
    }
    const pages = [];
    for (let i = Math.max(1, start); i <= end; i++) {
      pages.push(i);
    }
    return pages;
  };

  return (
    <div className={styles.container}>
      {/* 📍 헤더: 제목만 배치 */}
      <header className={styles.header}>
        <div className={styles.titleSection}>
          <LucideIcons.Box size={24} className={styles.titleIcon} />
          <h1>실시간 재고 현황</h1>
        </div>
      </header>

      {/* 📍 통계 섹션 */}
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <span className={styles.statLabel}>전체 품목 수</span>
          <span className={styles.statValue}>
            {isLoading ? "-" : allInventory.length.toLocaleString()}
          </span>
        </div>
        <div className={styles.statCard}>
          <span className={styles.statLabel}>재고 구매 필요(50개 이하)</span>
          <span className={`${styles.statValue} ${styles.warning}`}>
            {isLoading
              ? "-"
              : allInventory.filter((i) => (i?.current_quantity || 0) <= 50)
                  .length}
          </span>
        </div>
      </div>

      {/* 📍 테이블 컨트롤 섹션: 목록 바로 위로 이동 및 양 끝 정렬 */}
      <div className={styles.tableControls}>
        <div className={styles.searchBar}>
          <LucideIcons.Search size={18} />
          <input
            type="text"
            placeholder="부품 번호 또는 설명 검색..."
            value={searchTerm}
            onChange={handleSearchChange}
          />
        </div>

        <select
          className={styles.pageSizeSelect}
          value={pageSize}
          onChange={handlePageSizeChange}
        >
          <option value={10}>10개씩 보기</option>
          <option value={30}>30개씩 보기</option>
          <option value={50}>50개씩 보기</option>
        </select>
      </div>

      {/* 📍 데이터 테이블 영역 */}
      <div className={styles.tableWrapper}>
        {isLoading ? (
          <div className={styles.loading}>데이터 로딩 중...</div>
        ) : (
          <>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>부품 번호</th>
                  <th>설명</th>
                  <th>현재 수량</th>
                  <th>최종 업데이트</th>
                  <th>상태</th>
                </tr>
              </thead>
              <tbody>
                {displayInventory.length > 0 ? (
                  displayInventory.map((item) => (
                    <tr key={item.part_number}>
                      <td className={styles.partNum}>{item.part_number}</td>
                      <td>{item.description}</td>
                      <td className={styles.quantity}>
                        {(item.current_quantity ?? 0).toLocaleString()}
                      </td>
                      <td>{item.last_updated}</td>
                      <td>
                        <span
                          className={`${styles.badge} ${(item.current_quantity ?? 0) > 50 ? styles.safe : styles.danger}`}
                        >
                          {(item.current_quantity ?? 0) > 50 ? "정상" : "부족"}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className={styles.noData}>
                      데이터가 없습니다.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>

            {totalPages > 0 && (
              <div className={styles.pagination}>
                <button
                  onClick={goToFirst}
                  disabled={currentPage === 1}
                  title="첫 페이지"
                >
                  <LucideIcons.ChevronsLeft size={20} />
                </button>
                <button
                  onClick={jumpPrevTen}
                  disabled={currentPage === 1}
                  title="10페이지 뒤로"
                >
                  <LucideIcons.ChevronLeft size={20} />
                </button>
                {getPageNumbers().map((pageNum) => (
                  <button
                    key={pageNum}
                    className={currentPage === pageNum ? styles.activePage : ""}
                    onClick={() => setCurrentPage(pageNum)}
                  >
                    {pageNum}
                  </button>
                ))}
                <button
                  onClick={jumpNextTen}
                  disabled={currentPage === totalPages}
                  title="10페이지 앞으로"
                >
                  <LucideIcons.ChevronRight size={20} />
                </button>
                <button
                  onClick={goToLast}
                  disabled={currentPage === totalPages}
                  title="마지막 페이지"
                >
                  <LucideIcons.ChevronsRight size={20} />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default InventoryManagePage;
