# app/api/v1/controllers/dashboard_controller.py
from app.services.dashboard_service import DashboardService

class DashboardController:
    def __init__(self, service: DashboardService):
        self.service = service

    async def get_dashboard_summary(
        self, 
        year: int, 
        days: int, 
        top_y: int, 
        threshold: int
    ):
        """
        프론트엔드 대시보드 구성을 위한 종합 데이터 반환
        
        Args:
            year (int): 분석 대상 연도 (예: 2026)
            days (int): 상/하위 품목 분석 기준 기간 (일)
            top_y (int): 추출할 품목 개수
            threshold (int): 재고 부족으로 판단할 수량 기준
        """
        # Service 레이어를 호출하여 가공된 데이터를 가져옵니다.
        # 연도(year) 정보가 추가되어 메인 차트와 상세 차트가 동기화됩니다.
        summary_data = await self.service.get_summary(
            year=year,
            days=days,
            top_y=top_y,
            threshold=threshold
        )
        
        return summary_data