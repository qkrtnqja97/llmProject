# -*- coding: utf-8 -*-
"""
SQL 실행 모듈
- 데이터베이스 연결 및 쿼리 실행
- 결과 검증
- 캐싱
- Cloudflare Tunnel 자동 시작
"""

import re
import logging
import subprocess
import time
import psutil
import os
import shutil
import platform
from typing import Optional, Tuple

import pandas as pd
from sqlalchemy import create_engine, text, inspect

from api_llm.config import DATABASE_URL, DATABASE_CONFIG, SQL_CONFIG

logger = logging.getLogger(__name__)


def _get_training_logger():
    """지연 import (circular import 방지)"""
    from api_llm.utils.training_logger import log_training_data
    return log_training_data


class DatabaseManager:
    """데이터베이스 관리 (싱글톤)"""

    _instance = None
    _engine = None
    _connection_pool = None
    _cloudflared_process = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        # Cloudflare Tunnel 자동 시작
        self._start_cloudflared_if_needed()
        
        # 연결 안정화를 위해 잠시 대기
        time.sleep(2)
        
        self._initialize_engine()
        self._initialized = True

    def _start_cloudflared_if_needed(self):
        """Cloudflare Tunnel 클라이언트 자동 시작 (TCP 터널링)"""
        try:
            # .env에서 Cloudflare 원격 주소 읽기
            cloudflare_host = os.getenv("CLOUDFLARE_DB_HOST", "").strip()
            
            if not cloudflare_host or "trycloudflare.com" not in cloudflare_host:
                logger.debug("Cloudflare Tunnel 클라이언트가 필요하지 않음")
                return
            
            # 이미 cloudflared 실행 중인지 확인
            for proc in psutil.process_iter(['name']):
                if 'cloudflared' in proc.name().lower():
                    logger.info("✅ Cloudflare Tunnel 클라이언트가 이미 실행 중입니다")
                    return
            
            logger.info("🚀 Cloudflare Tunnel 클라이언트 자동 시작...")
            
            # cloudflared 경로 찾기
            cloudflared_path = shutil.which('cloudflared')
            
            if not cloudflared_path:
                logger.warning("⚠️  cloudflared를 찾을 수 없습니다")
                logger.warning("   다음을 실행하세요: choco install cloudflare-warp (또는 수동 설치)")
                return
            
            # 클라이언트 TCP 터널 명령어
            # cloudflared access tcp --hostname REMOTE_URL --url tcp://localhost:5432
            cmd = [
                cloudflared_path, "access", "tcp",
                "--hostname", cloudflare_host,
                "--url", "tcp://127.0.0.1:5432"
            ]
            
            # Windows에서 백그라운드 프로세스로 실행
            if platform.system() == "Windows":
                subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
                )
            else:
                # Unix/Linux
                subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    preexec_fn=lambda: os.setsid()
                )
            
            logger.info("✅ Cloudflare Tunnel 클라이언트 백그라운드에서 실행 중")
            logger.info(f"   원격: {cloudflare_host}:5432")
            logger.info(f"   로컬: 127.0.0.1:5432")
            logger.info("   (터널 준비에 5-10초 소요될 수 있습니다)")
            
            # 터널 안정화 시간
            time.sleep(3)
            
        except Exception as e:
            logger.warning(f"⚠️  Cloudflare Tunnel 자동 시작 실패: {str(e)[:100]}")

    def _initialize_engine(self):
        """SQLAlchemy 엔진 초기화 (커넥션 풀 포함)"""
        try:
            # Cloudflare 호스트인 경우 SSL 필수
            connect_args = {'connect_timeout': 10}
            if "trycloudflare.com" in DATABASE_CONFIG.get("HOST", ""):
                connect_args['sslmode'] = 'require'
            
            self._engine = create_engine(
                DATABASE_URL,
                connect_args=connect_args,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=1800,
                pool_pre_ping=True,
            )
            logger.info("✅ 데이터베이스 엔진 초기화 완료")
            
            # 스키마 설정 (database.py에서 지정한 스키마 사용)
            schema = DATABASE_CONFIG.get("SCHEMA", "public")
            if schema and schema != "public":
                try:
                    with self._engine.connect() as conn:
                        conn.execute(text(f"SET search_path TO {schema}"))
                        conn.commit()
                        logger.info(f"✅ PostgreSQL search_path 설정: {schema}")
                except Exception as e:
                    logger.warning(f"⚠️  스키마 설정 실패: {e}")
            
        except Exception as e:
            logger.exception(f"DB 엔진 초기화 실패: {e}")
            raise

    def get_engine(self):
        """엔진 반환"""
        return self._engine

    def get_column_map(self) -> dict:
        """
        테이블별 컬럼 맵 반환
        - inventory_mgmt 스키마: 모든 데이터 테이블
        - sql_assistant 스키마: conversations, request_logs 만
        """
        try:
            insp = inspect(self._engine)
            column_map = {}
            
            # 1. inventory_mgmt 스키마의 모든 테이블
            inventory_schema = "inventory_mgmt"
            try:
                for table in insp.get_table_names(schema=inventory_schema):
                    cols = [c['name'] for c in insp.get_columns(table, schema=inventory_schema)]
                    # 테이블명에 스키마 붙임
                    full_table = f"{inventory_schema}.{table}"
                    column_map[full_table] = cols
                    logger.debug(f"  ✅ {full_table}: {len(cols)}개 컬럼")
            except Exception as e:
                logger.warning(f"⚠️ {inventory_schema} 스키마 조회 실패: {e}")
            
            # 2. sql_assistant 스키마의 conversations, request_logs만
            assistant_schema = "sql_assistant"
            allowed_tables = ["conversations", "request_logs"]
            try:
                for table in insp.get_table_names(schema=assistant_schema):
                    if table in allowed_tables:
                        cols = [c['name'] for c in insp.get_columns(table, schema=assistant_schema)]
                        full_table = f"{assistant_schema}.{table}"
                        column_map[full_table] = cols
                        logger.debug(f"  ✅ {full_table}: {len(cols)}개 컬럼")
            except Exception as e:
                logger.warning(f"⚠️ {assistant_schema} 스키마 조회 실패: {e}")
            
            logger.info(f"✅ 컬럼 맵 로드: 총 {len(column_map)}개 테이블")
            for table in column_map.keys():
                logger.debug(f"   - {table}")
            
            return column_map
        except Exception as e:
            logger.exception("컬럼 맵 로드 실패")
            return {}

    def get_data_stats(self) -> dict:
        """
        데이터 통계 반환 (날짜 범위 등)
        - 실제 거래 데이터(sales_orders, purchase_orders)에서 날짜 범위 조회
        - initial_inventory 같은 스냅샷 테이블은 제외 (stock_date는 항상 2022-12-31)
        """
        try:
            schema = "inventory_mgmt"

            # 실제 거래 데이터가 있는 테이블/컬럼 우선순위
            TRANSACTION_TABLES = [
                (f"{schema}.sales_orders",    "sale_date"),
                (f"{schema}.purchase_orders", "purchase_date"),
            ]

            with self._engine.connect() as conn:
                global_min = None
                global_max = None

                for table_name, date_col in TRANSACTION_TABLES:
                    try:
                        result = conn.execute(
                            text(f"SELECT MIN({date_col}), MAX({date_col}) FROM {table_name}")
                        ).fetchone()
                        if result and result[0]:
                            t_min = str(result[0])
                            t_max = str(result[1])
                            if global_min is None or t_min < global_min:
                                global_min = t_min
                            if global_max is None or t_max > global_max:
                                global_max = t_max
                            logger.info(f"✅ 데이터 기간 조회 ({table_name}): {t_min} ~ {t_max}")
                    except Exception as e:
                        logger.debug(f"날짜 조회 스킵 [{table_name}]: {e}")

                if global_min and global_max:
                    logger.info(f"📅 최종 데이터 기간: {global_min} ~ {global_max}")
                    return {"min_date": global_min, "max_date": global_max}

                # fallback: 테이블이 없거나 실패 시 첫 번째 날짜 컬럼 탐색 (initial_inventory 제외)
                insp = inspect(self._engine)
                tables = insp.get_table_names(schema=schema)
                SKIP_TABLES = {"initial_inventory"}  # 스냅샷 테이블 제외

                for table in tables:
                    if table in SKIP_TABLES:
                        continue
                    cols = insp.get_columns(table, schema=schema)
                    for col in cols:
                        if any(k in col['name'].lower() for k in ['date', '_at', 'time']):
                            try:
                                result = conn.execute(
                                    text(f"SELECT MIN({col['name']}), MAX({col['name']}) FROM {schema}.{table}")
                                ).fetchone()
                                if result and result[0]:
                                    logger.info(f"✅ fallback 날짜 조회 ({schema}.{table}.{col['name']}): {result[0]} ~ {result[1]}")
                                    return {
                                        "min_date": str(result[0]),
                                        "max_date": str(result[1]),
                                    }
                            except Exception:
                                pass

                return {"min_date": "", "max_date": ""}

        except Exception as e:
            logger.warning(f"데이터 통계 조회 실패: {e}")
            return {"min_date": "", "max_date": ""}

    def execute_query(
        self,
        sql: str,
        question: Optional[str] = None,
        schema_snapshot: Optional[str] = None,
        enable_training_log: bool = True,
    ) -> Tuple[bool, pd.DataFrame, str]:
        """
        SQL 쿼리 실행
        
        Args:
            sql: SQL 쿼리
            question: 원본 사용자 질문 (로깅용)
            schema_snapshot: 스키마 정보 (로깅용)
            enable_training_log: 훈련 데이터 로깅 여부
        
        Returns:
            (성공 여부, DataFrame, 에러 메시지)
        """
        success = False
        df = None
        error_msg = ""
        
        try:
            with self._engine.connect() as conn:
                # inventory_mgmt 스키마 명시적 설정
                conn.execute(text("SET search_path TO inventory_mgmt"))
                
                # SELECT 쿼리에 LIMIT 추가 (없으면 서브쿼리로 감싸기)
                if not re.search(r'\bLIMIT\b', sql, re.IGNORECASE):
                    safe_sql = f"SELECT * FROM ({sql}) AS _sub LIMIT {SQL_CONFIG['QUERY_RESULT_LIMIT']}"
                else:
                    safe_sql = sql
                
                df = pd.read_sql_query(text(safe_sql), conn)
                logger.info(f"✅ 쿼리 실행 성공: {len(df)}행")
                success = True
        
        except Exception as e:
            error_msg = str(e)
            logger.exception(f"쿼리 실행 오류: {error_msg}")
            success = False
        
        # 훈련 데이터 로깅
        if enable_training_log and question:
            result_summary = f"{len(df)} rows" if success and df is not None else f"Error: {error_msg}"
            log_training_data = _get_training_logger()
            log_training_data(
                question=question,
                generated_sql=sql,
                schema_snapshot=schema_snapshot or "",
                execution_success=success,
                execution_result_summary=result_summary,
                user_satisfaction=None,  # UI에서 사용자 평가 받을 때 업데이트됨
                error_details=error_msg if not success else None,
            )
        
        # 대화 기록 저장 (맥락 파악용)
        if enable_training_log and question and success:
            from api_llm.utils.training_logger import save_conversation
            save_conversation(
                question=question,
                response_summary=f"{len(df)}행의 데이터를 반환했습니다.",
                sql_query=sql,
            )
        
        return success, df, error_msg


# 전역 인스턴스
_db_manager = None


def get_database_manager() -> DatabaseManager:
    """DB 매니저 싱글톤 반환"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def execute_sql(
    sql: str,
    question: Optional[str] = None,
    schema_snapshot: Optional[str] = None,
    enable_training_log: bool = True,
) -> Tuple[bool, pd.DataFrame, str]:
    """편의 함수: SQL 실행"""
    manager = get_database_manager()
    return manager.execute_query(
        sql,
        question=question,
        schema_snapshot=schema_snapshot,
        enable_training_log=enable_training_log,
    )


def get_column_map() -> dict:
    """편의 함수: 컬럼 맵"""
    manager = get_database_manager()
    return manager.get_column_map()


def get_data_stats() -> dict:
    """편의 함수: 데이터 통계"""
    manager = get_database_manager()
    return manager.get_data_stats()


def validate_result_dataframe(df: pd.DataFrame, question: str = "") -> Tuple[bool, list]:
    """
    결과 데이터 검증
    
    Returns:
        (is_valid, 이상사항_리스트)
    """
    anomalies = []
    
    if df is None or len(df) == 0:
        return True, []  # 0건은 이상이 아님 (없는 데이터)
    
    # NULL 비율 과다 (80%)
    for col in df.columns:
        null_ratio = df[col].isna().sum() / len(df)
        if null_ratio > 0.8:
            anomalies.append(f"'{col}' 컬럼 NULL {null_ratio:.0%} 초과.")
    
    # 음수 매출/수익
    for col in df.columns:
        if any(k in col.lower() for k in ['revenue', 'price', 'cost', 'profit', 'amount', '매출', '수익']):
            if pd.api.types.is_numeric_dtype(df[col]):
                neg = (df[col] < 0).sum()
                if neg > 0:
                    anomalies.append(f"'{col}' 음수값 {neg}건 (비즈니스 규칙 위반).")
    
    # 비정상 이상값 (평균의 10000배)
    for col in df.select_dtypes(include='number').columns:
        mean_v = df[col].mean()
        if mean_v > 0:
            max_v = df[col].max()
            if max_v > mean_v * 10000:
                anomalies.append(f"'{col}' 최대값({max_v:,.0f}) 비정상 감지.")
    
    if anomalies:
        logger.warning(f"데이터 이상 감지: {anomalies}")
        return False, anomalies
    
    return True, []


def sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame 수치형 데이터 정제 (차트 렌더링 오류 방지)"""
    if df is None or df.empty:
        return df
    
    clean_df = df.copy()
    for col in clean_df.columns:
        converted = pd.to_numeric(clean_df[col], errors='coerce')
        if not converted.isna().all():
            clean_df[col] = converted.fillna(0)
    
    return clean_df
