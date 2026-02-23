import React from "react";

const InsightPage: React.FC = () => {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">인사이트</h2>
      <p className="text-xs text-zinc-500">
        회의록, 로그, 발주/재고 데이터를 기반으로 자동 생성된 요약과 리포트를
        모아보는 영역입니다. 지금은 레이아웃 목업 단계입니다.
      </p>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl shadow-sm p-4 text-xs">
          <p className="text-[11px] text-zinc-400 mb-1">재고 트렌드</p>
          <p className="font-semibold mb-2">
            베어링 계열 부품 소진 속도 증가 (지난달 대비 +18%)
          </p>
          <p className="text-zinc-500">
            생산 계획 조정과 안전재고 상향이 필요하다는 리포트가 자동
            생성됩니다.
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm p-4 text-xs">
          <p className="text-[11px] text-zinc-400 mb-1">회의 요약</p>
          <p className="font-semibold mb-2">
            주간 생산·자재 회의 핵심 의사결정 3건
          </p>
          <p className="text-zinc-500">
            RAG로 불러온 회의록에서 액션 아이템과 담당자를 추려 보여줍니다.
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm p-4 text-xs">
          <p className="text-[11px] text-zinc-400 mb-1">리스크 알림</p>
          <p className="font-semibold mb-2">
            3주 내 납기 지연 가능성이 높은 발주 4건
          </p>
          <p className="text-zinc-500">
            공급사 리드타임과 과거 지연 데이터를 기반으로 위험 발주를
            하이라이트합니다.
          </p>
        </div>
      </div>
    </div>
  );
};

export default InsightPage;