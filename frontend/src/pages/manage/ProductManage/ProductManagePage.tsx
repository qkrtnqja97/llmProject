import React, { useState, useEffect, useCallback } from "react";
import * as LucideIcons from "lucide-react";
import styles from "./ProductManagePage.module.css";
import { inventoryService, ProductItem } from "@services/inventoryService";
import ProductDetailModal from "@components/modals/ProductDetailModal";

const ProductManagePage = () => {
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  // 📍 모달 상태 및 상세 데이터 로딩 상태
  const [selectedProduct, setSelectedProduct] = useState<ProductItem | null>(
    null,
  );
  const [isDetailLoading, setIsDetailLoading] = useState(false);

  // 페이지네이션 상태
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  // 1. 제품 목록 로드
  const fetchProducts = useCallback(async () => {
    try {
      setIsLoading(true);
      const skip = (currentPage - 1) * pageSize;
      const response = await inventoryService.getProducts(
        skip,
        pageSize,
        searchTerm,
      );
      setProducts(response?.items || []);
      setTotalCount(response?.total || 0);
    } catch (error) {
      console.error("제품 로드 실패:", error);
      setProducts([]);
      setTotalCount(0);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, pageSize, searchTerm]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  // 2. 📍 상세보기 핸들러 (API 재호출로 최신 JOIN 데이터 확보)
  const handleShowDetail = async (partNumber: string) => {
    try {
      setIsDetailLoading(true);
      // 상세 조회 API 호출 (백엔드 get_product_by_id 실행)
      const detailedData = await inventoryService.getProductDetail(partNumber);
      setSelectedProduct(detailedData);
    } catch (error) {
      console.error("상세 정보 로드 실패:", error);
      alert("제품 정보를 가져오는데 실패했습니다.");
    } finally {
      setIsDetailLoading(false);
    }
  };

  // 페이지네이션 로직
  const totalPages = Math.ceil(totalCount / pageSize);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  const handlePageSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setPageSize(Number(e.target.value));
    setCurrentPage(1);
  };

  const jumpNextTen = () =>
    setCurrentPage((prev) => Math.min(prev + 10, totalPages));
  const jumpPrevTen = () => setCurrentPage((prev) => Math.max(prev - 10, 1));
  const goToFirst = () => setCurrentPage(1);
  const goToLast = () => setCurrentPage(totalPages);

  const getPageNumbers = () => {
    const pageLimit = 5;
    let start = Math.max(1, currentPage - Math.floor(pageLimit / 2));
    let end = Math.min(totalPages, start + pageLimit - 1);
    if (end - start + 1 < pageLimit) start = Math.max(1, end - pageLimit + 1);
    const pages = [];
    for (let i = Math.max(1, start); i <= end; i++) pages.push(i);
    return pages;
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.titleSection}>
          <LucideIcons.Package size={28} className={styles.titleIcon} />
          <h1>제품 카탈로그 관리</h1>
        </div>
        <button className={styles.addBtn}>
          <LucideIcons.Plus size={18} /> 제품 등록
        </button>
      </header>

      {/* 📍 컨트롤 섹션: 헤더 밖으로 이동, 검색창(좌) / 개수선택(우) 배치 */}
      <div className={styles.tableControls}>
        <div className={styles.searchBar}>
          <LucideIcons.Search size={18} />
          <input
            type="text"
            placeholder="제품 이름 또는 번호 검색..."
            value={searchTerm}
            onChange={handleSearchChange}
          />
        </div>

        <select
          className={styles.pageSizeSelect}
          value={pageSize}
          onChange={handlePageSizeChange}
        >
          <option value={20}>20개씩 보기</option>
          <option value={50}>50개씩 보기</option>
          <option value={100}>100개씩 보기</option>
        </select>
      </div>

      {isLoading ? (
        <div className={styles.loading}>제품 정보를 불러오는 중...</div>
      ) : (
        <>
          <div className={styles.productGrid}>
            {products.length > 0 ? (
              products.map((product) => (
                <div key={product.part_number} className={styles.productCard}>
                  <div className={styles.imagePlaceholder}>
                    <LucideIcons.Image size={24} strokeWidth={1.5} />
                  </div>
                  <div className={styles.productInfo}>
                    <span className={styles.partBadge}>
                      {product.part_number}
                    </span>
                    <h3 className={styles.productName}>
                      {product.description || "설명 없음"}
                    </h3>
                    <div className={styles.priceRow}>
                      <span className={styles.priceValue}>
                        ￦{Number(product.std_selling_price).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <button
                    className={styles.detailBtn}
                    disabled={isDetailLoading}
                    onClick={() => handleShowDetail(product.part_number)}
                  >
                    상세보기
                  </button>
                </div>
              ))
            ) : (
              <div className={styles.noData}>조회된 제품이 없습니다.</div>
            )}
          </div>

          {totalPages > 0 && (
            <div className={styles.pagination}>
              <button onClick={goToFirst} disabled={currentPage === 1}>
                <LucideIcons.ChevronsLeft size={20} />
              </button>
              <button onClick={jumpPrevTen} disabled={currentPage === 1}>
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
              >
                <LucideIcons.ChevronRight size={20} />
              </button>
              <button onClick={goToLast} disabled={currentPage === totalPages}>
                <LucideIcons.ChevronsRight size={20} />
              </button>
            </div>
          )}
        </>
      )}

      {/* 📍 상세 정보 모달 */}
      <ProductDetailModal
        product={selectedProduct}
        onClose={() => setSelectedProduct(null)}
      />
    </div>
  );
};

export default ProductManagePage;
