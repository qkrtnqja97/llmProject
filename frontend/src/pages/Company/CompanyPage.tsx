import React, { useState } from "react";
import { useCompany } from "../../context/CompanyContext";
// ✅ CSS Modules 임포트
import styles from "./CompanyPage.module.css";
import common from "../../app/styles/Global.module.css";

const CompanyPage: React.FC = () => {
  const { company, updateCompany } = useCompany();
  const [form, setForm] = useState(company);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    updateCompany(form);
    alert("회사 정보가 업데이트되었습니다.");
  };

  return (
    <div className={styles.gridContainer}>
      {/* 왼쪽: 설정 카드 */}
      <div className={common.pageSectionCard}>
        <h3 className={common.pageTitle}>시스템 환경 설정</h3>

        <form onSubmit={handleSave} className={styles.form}>
          <div className={styles.fieldGroup}>
            <label className={styles.label}>서비스명</label>
            <input
              className={styles.input}
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>

          <div className={styles.fieldGroup}>
            <label className={styles.label}>로고 URL</label>
            <input
              className={styles.input}
              value={form.logoUrl || ""}
              onChange={(e) => setForm({ ...form, logoUrl: e.target.value })}
              placeholder="https://..."
            />
          </div>

          <button type="submit" className={styles.saveBtn}>
            설정 저장
          </button>
        </form>
      </div>

      {/* 오른쪽: 프리뷰 카드 */}
      <div className={styles.previewCard}>
        <p className={styles.previewLabel}>Sidebar Preview</p>
        <div className={styles.sidebarPreview}>
          <div className={styles.previewLogo}>
            {form.logoUrl ? (
              <img
                src={form.logoUrl}
                alt="Logo"
                style={{ width: "100%", height: "100%", objectFit: "contain" }}
              />
            ) : (
              form.name.slice(0, 2).toUpperCase()
            )}
          </div>
          <span className={styles.previewName}>{form.name}</span>
        </div>
      </div>
    </div>
  );
};

export default CompanyPage;
