# app/services/dashboard_service.py
from app.repositories.dashboard_repository import DashboardRepository

class DashboardService:
    def __init__(self, dashboard_repo: DashboardRepository):
        self.dashboard_repo = dashboard_repo

    async def get_summary(self, year: int, days: int, top_y: int, threshold: int):
        """
        대시보드 종합 데이터 가공 서비스
        - 메인 차트: 시스템 전체 히스토리 (전체 기간)
        - 리스트/상세 차트: 선택된 연도(year) 기준 필터링
        """
        
        # 1. [리스트] 성과 상위/하위 품목 조회 (선택된 연도의 실적 합계 기준)
        # 📍 Repository 인터페이스에 맞춰 year와 top_y 전달 (days는 연도 분석 시 불필요하여 제외 가능)
        top_sales = await self.dashboard_repo.get_top_sales(year=year, top_y=top_y)
        bottom_sales = await self.dashboard_repo.get_bottom_sales(year=year, top_y=top_y)

        # 2. [상세 차트] 추출된 품목별 월별 트렌드 데이터 할당
        # 선택된 연도(year)의 1월~12월 데이터를 가져와서 각 아이템 객체에 병합합니다.
        for item in top_sales:
            item["monthlyTrend"] = await self.dashboard_repo.get_product_monthly_trend(
                part_number=item["id"], 
                year=year
            )
            
        for item in bottom_sales:
            item["monthlyTrend"] = await self.dashboard_repo.get_product_monthly_trend(
                part_number=item["id"], 
                year=year
            )
        
        # 3. [메인 차트] 시스템 전체 시계열 경영 실적 (필터 없음)
        monthly_stats = await self.dashboard_repo.get_monthly_profit_loss()
        
        # 4. [패턴 분석] 요일별 판매 빈도 분석
        weekly_pattern = await self.dashboard_repo.get_weekly_sales_pattern()

        # 5. [재고 알림] 설정된 임계치(threshold) 이하 품목 조회 
        low_inventory = await self.dashboard_repo.get_low_inventory(threshold)

        # 6. [일정] 캘린더 이벤트 데이터 조회
        upcoming_events = await self.dashboard_repo.get_calendar_events()

        # 최종 데이터 구조 조합하여 반환
        return {
            "topSales": top_sales,
            "botSales": bottom_sales,
            "monthlyStats": monthly_stats,
            "weeklyPattern": [dict(r) for r in weekly_pattern], # asyncpg.Record 변환
            "lowInventory": low_inventory, 
            "upcomingEvents": upcoming_events
        }