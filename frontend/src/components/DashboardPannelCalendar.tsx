// src/components/DashboardPannelCalendar.tsx
import React, { useState } from "react";
import Calendar from "react-calendar";
import { AlertTriangle, CheckCircle2, Box, ShoppingCart } from "lucide-react";

// ✅ 캘린더 값: 일단 any로 느슨하게 (타입스트레스 방지용)
export const DashboardPanel: React.FC = () => {
  const [date, setDate] = useState<any>(new Date());

  return (
    <section className="bg-white rounded-3xl shadow-sm border flex flex-col h-full">
      {/* 상단 */}
      <div className="px-5 py-4 border-b flex items-center justify-between">
        <div>
          <div className="text-sm font-semibold">오늘의 인사이트</div>
          <div className="text-xs text-zinc-500">
            업무 진행률, 재고 현황, 일정 정보를 한 번에 확인하세요.
          </div>
        </div>
      </div>

      {/* 내용 */}
      <div className="flex-1 overflow-auto px-5 py-4 space-y-4">
        {/* 인사이트 카드 */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <InsightCard
            icon={<CheckCircle2 className="w-4 h-4 text-emerald-500" />}
            label="오늘 업무 완료율"
            value="68%"
            sub="5/8건 완료"
          />
          <InsightCard
            icon={<AlertTriangle className="w-4 h-4 text-amber-500" />}
            label="재고 부족 상품"
            value="3개"
            sub="발주 필요"
          />
          <InsightCard
            icon={<Box className="w-4 h-4 text-indigo-500" />}
            label="전체 재고 수량"
            value="1,240"
            sub="창고 A · B 포함"
          />
          <InsightCard
            icon={<ShoppingCart className="w-4 h-4 text-sky-500" />}
            label="진행 중 발주"
            value="4건"
            sub="2건 지연"
          />
        </div>

        {/* 캘린더 */}
        <div className="border rounded-2xl p-3">
          <div className="flex items-center justify-between mb-2">
            <div className="text-xs font-semibold">캘린더 / 플래너</div>
            <div className="text-[11px] text-zinc-500">
              일정은 추후 API 연동 예정
            </div>
          </div>
          <Calendar
            value={date as any}                          // ✅ any 캐스팅
            onChange={(nextValue: any) => setDate(nextValue)} // ✅ any로 받아서 상태 업데이트
            locale="ko-KR"
            className="text-[11px]"
          />
        </div>
      </div>
    </section>
  );
};

type InsightCardProps = {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub?: string;
};

const InsightCard: React.FC<InsightCardProps> = ({ icon, label, value, sub }) => {
  return (
    <div className="border rounded-2xl px-3 py-2 bg-zinc-50 flex flex-col gap-1">
      <div className="flex items-center justify-between">
        <span className="text-[11px] text-zinc-500">{label}</span>
        {icon}
      </div>
      <div className="text-sm font-semibold">{value}</div>
      {sub && <div className="text-[11px] text-zinc-400">{sub}</div>}
    </div>
  );
};