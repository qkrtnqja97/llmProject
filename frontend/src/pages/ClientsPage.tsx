import React from "react";

const clients = [
  {
    name: "ABC 패션",
    contact: "김민수 팀장",
    email: "minsu.kim@abcfashion.com",
    phone: "010-1234-5678",
    memo: "온라인 매장 위주, 월 2회 발주",
  },
  {
    name: "XYZ 리테일",
    contact: "이서준 매니저",
    email: "seojun.lee@xyzretail.com",
    phone: "010-2222-3333",
    memo: "리드타임 민감, 재고 부족 알림 요청",
  },
  {
    name: "Studio ON",
    contact: "박하늘 대표",
    email: "haneul@studioon.kr",
    phone: "010-9876-5432",
    memo: "신규 상품 샘플 우선 발송",
  },
];

const ClientsPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#f3f4f6] p-8">
      <div className="max-w-5xl mx-auto bg-white rounded-3xl shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-lg font-semibold tracking-tight">
              고객사 연락처
            </h1>
            <p className="text-xs text-zinc-500 mt-1">
              주요 고객사의 담당자 정보와 간단 메모를 관리합니다.
            </p>
          </div>
          <button className="px-3 py-1.5 rounded-xl border text-xs hover:bg-zinc-50">
            + 고객사 추가
          </button>
        </div>

        <div className="mt-3 border rounded-2xl overflow-hidden text-xs">
          <div className="grid grid-cols-[2fr_1.4fr_2fr_1.4fr_2.2fr] bg-zinc-50 px-3 py-2 text-zinc-500">
            <span>고객사</span>
            <span>담당자</span>
            <span>이메일</span>
            <span>연락처</span>
            <span>메모</span>
          </div>
          {clients.map((c, idx) => (
            <div
              key={c.name}
              className={`grid grid-cols-[2fr_1.4fr_2fr_1.4fr_2.2fr] px-3 py-2 items-center ${
                idx % 2 === 1 ? "bg-zinc-50/60" : "bg-white"
              }`}
            >
              <span className="font-medium">{c.name}</span>
              <span>{c.contact}</span>
              <span className="truncate">{c.email}</span>
              <span>{c.phone}</span>
              <span className="truncate text-zinc-500">{c.memo}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ClientsPage;