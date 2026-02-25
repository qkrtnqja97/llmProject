// src/context/CompanyContext.tsx
import React, { createContext, useContext, useState } from "react";
import type { CompanyInfo } from "../shared/types";

interface CompanyContextType {
  company: CompanyInfo;
  updateCompany: (info: CompanyInfo) => void; // ✅ setCompany에서 명칭 변경
}

const CompanyContext = createContext<CompanyContextType | undefined>(undefined);

export const CompanyProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [company, setCompany] = useState<CompanyInfo>({
    name: "biz ai",
    logoUrl: "",
    address: "서울특별시 강남구",
  });

  const updateCompany = (info: CompanyInfo) => {
    setCompany(info);
  };

  return (
    <CompanyContext.Provider value={{ company, updateCompany }}>
      {children}
    </CompanyContext.Provider>
  );
};

export const useCompany = () => {
  const context = useContext(CompanyContext);
  if (!context) throw new Error("useCompany error");
  return context;
};
