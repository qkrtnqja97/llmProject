import React, { useState, type FormEvent } from "react";
import { useCompany } from "../context/CompanyContext";

const CompanyPage: React.FC = () => {
  const { company, setCompany } = useCompany();
  const [name, setName] = useState(company.name);
  const [address, setAddress] = useState(company.address ?? "");
  const [logoUrl, setLogoUrl] = useState(company.logoUrl ?? "");
  const [slogan, setSlogan] = useState("데이터 기반 의사결정 파트너");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setCompany({ name: name || "biz ai", address, logoUrl });
  };

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-3xl shadow-sm p-6 space-y-4"
      >
        <h2 className="text-lg font-semibold mb-2">회사 정보</h2>

        <div className="space-y-1 text-sm">
          <label className="text-xs text-zinc-500">회사명</label>
          <input
            className="w-full border rounded-xl px-3 py-2 text-sm"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="예: biz ai"
          />
        </div>

        <div className="space-y-1 text-sm">
          <label className="text-xs text-zinc-500">주소</label>
          <input
            className="w-full border rounded-xl px-3 py-2 text-sm"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="예: 서울특별시 어딘가 123"
          />
        </div>

        <div className="space-y-1 text-sm">
          <label className="text-xs text-zinc-500">로고 이미지 URL</label>
          <input
            className="w-full border rounded-xl px-3 py-2 text-sm"
            value={logoUrl}
            onChange={(e) => setLogoUrl(e.target.value)}
            placeholder="https://... 형식의 이미지 주소"
          />
        </div>

        <div className="space-y-1 text-sm">
          <label className="text-xs text-zinc-500">슬로건</label>
          <input
            className="w-full border rounded-xl px-3 py-2 text-sm"
            value={slogan}
            onChange={(e) => setSlogan(e.target.value)}
          />
        </div>

        <button
          type="submit"
          className="mt-2 px-4 py-2 rounded-xl bg-zinc-900 text-white text-sm"
        >
          저장
        </button>
      </form>

      <div className="bg-white rounded-3xl shadow-sm p-6 flex flex-col items-center justify-center text-center">
        <p className="text-xs text-zinc-400 mb-2">미리보기</p>
        <div className="flex items-center gap-3 mb-3">
          {logoUrl ? (
            <img
              src={logoUrl}
              alt={name}
              className="w-10 h-10 rounded-full object-cover shadow-sm"
            />
          ) : (
            <div className="w-10 h-10 rounded-full bg-zinc-900 text-white flex items-center justify-center text-sm font-bold">
              {name.slice(0, 2).toUpperCase()}
            </div>
          )}
          <div className="flex flex-col items-start">
            <span className="font-semibold text-sm">{name || "biz ai"}</span>
            <span className="text-[11px] text-zinc-500">{slogan}</span>
          </div>
        </div>
        <p className="text-[11px] text-zinc-500">
          이 로고와 이름은 좌측 상단 사이드바와 일부 페이지 헤더에 사용됩니다.
        </p>
      </div>
    </div>
  );
};

export default CompanyPage;