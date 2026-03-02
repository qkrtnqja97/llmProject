import { useEffect } from "react";
import * as LucideIcons from "lucide-react";
import { ProductItem } from "@services/inventoryService";
import styles from "./ProductDetailModal.module.css";

interface ProductDetailModalProps {
  product: ProductItem | null;
  onClose: () => void;
}

const ProductDetailModal = ({ product, onClose }: ProductDetailModalProps) => {
  // 📍 1. Esc 키 감지 로직 (기능 유지)
  useEffect(() => {
    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    if (product) {
      window.addEventListener("keydown", handleEsc);
    }

    return () => {
      window.removeEventListener("keydown", handleEsc);
    };
  }, [product, onClose]);

  if (!product) return null;

  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modalContent}>
        <div className={styles.modalHeader}>
          <h2>제품 상세 정보</h2>
          <button className={styles.closeBtn} onClick={onClose}>
            <LucideIcons.X size={24} />
          </button>
        </div>

        <div className={styles.modalBody}>
          <div className={styles.modalImage}>
            {/* 📍 테마 대응: 아이콘 색상을 CSS에서 제어할 수 있도록 className 추가 */}
            <LucideIcons.Image
              size={60}
              strokeWidth={1}
              className={styles.imageIcon}
            />
          </div>

          <div className={styles.modalInfoList}>
            <div className={styles.infoItem}>
              <label>부품 번호</label>
              <span className={styles.partNum}>{product.part_number}</span>
            </div>

            <div className={styles.infoItem}>
              <label>부품명(설명)</label>
              <span className={styles.descText}>
                {product.description || "설명 없음"}
              </span>
            </div>

            <div className={styles.infoItem}>
              <label>제조사</label>
              <span>{product.manufacturer || "정보 없음"}</span>
            </div>

            <div className={styles.infoItem}>
              <label>현재 재고량</label>
              <span className={styles.stockValue}>
                {(product.current_quantity ?? 0).toLocaleString()} EA
              </span>
            </div>

            <div className={styles.infoItem}>
              <label>표준 판매가</label>
              <span className={styles.priceValue}>
                ￦{(product.std_selling_price || 0).toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        <div className={styles.modalFooter}>
          <button className={styles.editBtn}>정보 수정</button>
          <button className={styles.confirmBtn} onClick={onClose}>
            확인
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailModal;
