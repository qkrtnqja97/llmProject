# routes/dashboard_router.py
from fastapi import APIRouter, Depends, Query
from app.api.deps import get_dashboard_controller
from app.api.v1.controllers.dashboard_controller import DashboardController

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
async def get_summary(
    year: int = Query(2026, description="분석 대상 연도 (예: 2026)"),
    days: int = Query(7, description="상/하위 품목 분석 기준 기간 (일)"),
    top_y: int = Query(3, description="추출할 품목 개수"),
    threshold: int = Query(5, description="재고 부족 판단 수량 기준"),
    controller: DashboardController = Depends(get_dashboard_controller)
):
    """
    대시보드 종합 데이터 조회 엔드포인트
    - year: 메인 경영 실적 및 품목 상세 분석 그래프의 기준 연도
    - days/top_y: 성과 상/하위 품목 추출 기준
    - threshold: 재고 부족 알림 기준
    """
    return await controller.get_dashboard_summary(
        year=year,
        days=days, 
        top_y=top_y, 
        threshold=threshold
    )