import React, { createContext, useContext, useState } from "react";

export type CompanyInfo = {
  name: string;
  address?: string;
  logoUrl?: string;
};

type CompanyContextValue = {
  company: CompanyInfo;
  setCompany: (info: CompanyInfo) => void;
};

const CompanyContext = createContext<CompanyContextValue | undefined>(
  undefined,
);

const defaultCompany: CompanyInfo = {
  name: "biz ai",
};

export const CompanyProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [company, setCompany] = useState<CompanyInfo>(defaultCompany);

  return (
    <CompanyContext.Provider value={{ company, setCompany }}>
      {children}
    </CompanyContext.Provider>
  );
};

export const useCompany = (): CompanyContextValue => {
  const ctx = useContext(CompanyContext);
  if (!ctx) throw new Error("useCompany must be used within CompanyProvider");
  return ctx;
};