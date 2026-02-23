import React from "react";

const DashboardPage: React.FC = () => {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">부품 운영 대시보드</h2>
      <p className="text-xs text-zinc-500">
        주요 지표와 발주·회의 정보를 한 번에 확인할 수 있는 화면입니다.
      </p>

      {/* 👉 여기 아래에 기존 KPI 카드 + 테이블 + AI Copilot 요약 카드 붙이면 됨 */}
      {/* 지금 LlmDashboard 안쪽 content 부분을 이쪽으로 복붙 */}
    </div>
  );
};

export default DashboardPage;