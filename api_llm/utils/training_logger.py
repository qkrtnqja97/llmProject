# -*- coding: utf-8 -*-
"""
훈련 데이터 로거
- DB (sql_assistant 스키마) + JSON Lines 형식으로 쿼리 기록 저장
- request_logs: 모든 요청 로그 (무한 쌓임, 학습용)
- conversations: 최근 1개월 대화 (맥락 파악용)
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from sqlalchemy import text

logger = logging.getLogger(__name__)

# 로깅 디렉토리
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
TRAINING_LOG_FILE = LOGS_DIR / "training_data.jsonl"


def ensure_log_dir():
    """로그 디렉토리 생성"""
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"로그 디렉토리 생성 실패: {e}")


def log_training_data(
    question: str,
    generated_sql: str,
    schema_snapshot: str,
    execution_success: bool,
    execution_result_summary: str,
    user_satisfaction: Optional[int] = None,
    error_details: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    훈련 데이터 로깅
    - 파일 (JSONL): 로컬 백업
    - DB: sql_assistant.request_logs
    
    Args:
        question: 사용자 질문
        generated_sql: 생성된 SQL
        schema_snapshot: 테이블 스키마 정보
        execution_success: 실행 성공 여부
        execution_result_summary: 결과 요약 (행 수, 에러 메시지 등)
        user_satisfaction: 사용자 만족도 (1: 좋아요, 0: 없음, -1: 싫어요, None: 평가 안함)
        error_details: 에러 상세 정보
        metadata: 추가 메타데이터
    
    Returns:
        bool: 로깅 성공 여부
    """
    try:
        ensure_log_dir()
        timestamp = datetime.now().isoformat()
        
        record = {
            "timestamp": timestamp,
            "question": question,
            "generated_sql": generated_sql,
            "schema_snapshot": schema_snapshot,
            "execution_success": execution_success,
            "execution_result_summary": execution_result_summary,
            "user_satisfaction": user_satisfaction,
        }
        
        if error_details:
            record["error_details"] = error_details
        
        if metadata:
            record["metadata"] = metadata
        
        # 1. JSONL 파일에 추가 (백업)
        with open(TRAINING_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        logger.debug(f"✅ 훈련 데이터 파일 로깅: {question[:50]}...")
        
        # 2. DB에 저장 (sql_assistant.request_logs)
        try:
            from api_llm.sql.sql_executor import get_database_manager
            manager = get_database_manager()
            
            with manager.get_engine().connect() as conn:
                insert_query = text("""
                    INSERT INTO sql_assistant.request_logs 
                    (question, generated_sql, schema_snapshot, execution_success, 
                     execution_result_summary, user_satisfaction, error_details, metadata, created_at)
                    VALUES (:question, :generated_sql, :schema_snapshot, :execution_success,
                            :execution_result_summary, :user_satisfaction, :error_details, :metadata, :created_at)
                """)
                
                conn.execute(
                    insert_query,
                    {
                        "question": question,
                        "generated_sql": generated_sql,
                        "schema_snapshot": schema_snapshot,
                        "execution_success": execution_success,
                        "execution_result_summary": execution_result_summary,
                        "user_satisfaction": user_satisfaction,
                        "error_details": error_details,
                        "metadata": json.dumps(metadata, ensure_ascii=False) if metadata else None,
                        "created_at": datetime.now(),
                    }
                )
                conn.commit()
                logger.debug(f"✅ 훈련 데이터 DB 저장: {question[:50]}...")
        except Exception as db_err:
            logger.warning(f"⚠️ DB 저장 실패 (파일 백업으로 유지): {str(db_err)[:100]}")
        
        return True
    
    except Exception as e:
        logger.error(f"훈련 데이터 로깅 실패: {e}")
        return False


def get_recent_conversations(limit: int = 5) -> list:
    """
    최근 대화 기록 조회 (맥락 파악용)
    - DB: sql_assistant.conversations 테이블
    - 최신순 정렬, 필요한 필드만 추출
    
    Args:
        limit: 조회할 최근 대화 수
    
    Returns:
        list: [{"question": "...", "timestamp": "...", "response_summary": "..."}, ...]
    """
    try:
        from api_llm.sql.sql_executor import get_database_manager
        manager = get_database_manager()
        
        with manager.get_engine().connect() as conn:
            query = text("""
                SELECT question, response_summary, created_at
                FROM sql_assistant.conversations
                WHERE created_at >= NOW() - INTERVAL '1 month'
                ORDER BY created_at DESC
                LIMIT :limit
            """)
            
            result = conn.execute(query, {"limit": limit})
            conversations = []
            
            for row in result:
                conversations.append({
                    "question": row[0],
                    "response_summary": row[1],
                    "timestamp": row[2].isoformat() if row[2] else "",
                })
            
            # 최신순으로 정렬된 것을 역순으로 (오래된 순 → 최신순)
            conversations.reverse()
            
            logger.debug(f"✅ 대화 조회: {len(conversations)}건")
            return conversations
    
    except Exception as e:
        logger.warning(f"⚠️ 대화 조회 실패 (빈 리스트 반환): {str(e)[:100]}")
        return []


def save_conversation(
    question: str,
    response_summary: str,
    refined_question: Optional[str] = None,
    sql_query: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    대화 기록 저장 (맥락 파악용)
    - DB에만 저장: sql_assistant.conversations
    - 최근 1개월 데이터만 유지 (자동 삭제)
    
    Args:
        question: 사용자 질문
        response_summary: 응답 요약
        refined_question: 정제된 질문
        sql_query: SQL 쿼리
        metadata: 추가 메타데이터
    
    Returns:
        bool: 저장 성공 여부
    """
    try:
        from api_llm.sql.sql_executor import get_database_manager
        manager = get_database_manager()
        
        with manager.get_engine().connect() as conn:
            # 1. 새 대화 저장
            insert_query = text("""
                INSERT INTO sql_assistant.conversations 
                (question, response_summary, refined_question, sql_query, metadata, created_at)
                VALUES (:question, :response_summary, :refined_question, :sql_query, :metadata, :created_at)
            """)
            
            conn.execute(
                insert_query,
                {
                    "question": question,
                    "response_summary": response_summary,
                    "refined_question": refined_question,
                    "sql_query": sql_query,
                    "metadata": json.dumps(metadata, ensure_ascii=False) if metadata else None,
                    "created_at": datetime.now(),
                }
            )
            
            # 2. 1개월 이상 된 데이터 자동 삭제
            delete_query = text("""
                DELETE FROM sql_assistant.conversations
                WHERE created_at < NOW() - INTERVAL '1 month'
            """)
            
            delete_result = conn.execute(delete_query)
            conn.commit()
            
            deleted_count = delete_result.rowcount
            if deleted_count > 0:
                logger.info(f"✅ 대화 저장 및 {deleted_count}건 오래된 데이터 삭제")
            else:
                logger.debug(f"✅ 대화 저장 (삭제할 오래된 데이터 없음)")
            
            return True
    
    except Exception as e:
        logger.error(f"대화 저장 실패: {e}")
        return False


def get_training_log_stats() -> Dict[str, Any]:
    """
    로깅 통계 조회
    
    Returns:
        dict: 총 로그 수, 성공률, 만족도 평균 등
    """
    try:
        if not TRAINING_LOG_FILE.exists():
            return {
                "total_logs": 0,
                "success_rate": 0.0,
                "avg_satisfaction": None,
                "file_path": str(TRAINING_LOG_FILE),
            }
        
        total = 0
        success_count = 0
        satisfaction_scores = []
        
        with open(TRAINING_LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        total += 1
                        if record.get("execution_success"):
                            success_count += 1
                        if record.get("user_satisfaction") is not None:
                            satisfaction_scores.append(record["user_satisfaction"])
                    except json.JSONDecodeError:
                        continue
        
        avg_satisfaction = (
            sum(satisfaction_scores) / len(satisfaction_scores)
            if satisfaction_scores
            else None
        )
        
        return {
            "total_logs": total,
            "success_rate": (success_count / total * 100) if total > 0 else 0.0,
            "avg_satisfaction": round(avg_satisfaction, 2) if avg_satisfaction else None,
            "satisfaction_count": len(satisfaction_scores),
            "file_path": str(TRAINING_LOG_FILE),
        }
    
    except Exception as e:
        logger.error(f"통계 조회 실패: {e}")
        return {"error": str(e)}


def export_training_dataset(
    output_format: str = "jsonl",
    success_only: bool = False,
    with_satisfaction_only: bool = False,
) -> Optional[str]:
    """
    훈련용 데이터셋 내보내기
    
    Args:
        output_format: 'jsonl' 또는 'json'
        success_only: 성공한 쿼리만 포함
        with_satisfaction_only: 사용자 평가가 있는 것만 포함
    
    Returns:
        str: 내보낸 파일 경로, 실패시 None
    """
    try:
        if not TRAINING_LOG_FILE.exists():
            logger.warning("훈련 데이터가 없습니다")
            return None
        
        records = []
        with open(TRAINING_LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        
                        if success_only and not record.get("execution_success"):
                            continue
                        if with_satisfaction_only and record.get("user_satisfaction") is None:
                            continue
                        
                        records.append(record)
                    except json.JSONDecodeError:
                        continue
        
        # 내보내기
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_format == "json":
            export_file = LOGS_DIR / f"training_dataset_{timestamp}.json"
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        else:  # jsonl
            export_file = LOGS_DIR / f"training_dataset_{timestamp}.jsonl"
            with open(export_file, "w", encoding="utf-8") as f:
                for record in records:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        logger.info(f"✅ 데이터셋 내보내기: {export_file}")
        return str(export_file)
    
    except Exception as e:
        logger.error(f"데이터셋 내보내기 실패: {e}")
        return None


def get_training_log_stats() -> Dict[str, Any]:
    """
    로깅 통계 조회
    
    Returns:
        dict: 총 로그 수, 성공률, 만족도 평균 등
    """
    try:
        if not TRAINING_LOG_FILE.exists():
            return {
                "total_logs": 0,
                "success_rate": 0.0,
                "avg_satisfaction": None,
                "file_path": str(TRAINING_LOG_FILE),
            }
        
        total = 0
        success_count = 0
        satisfaction_scores = []
        
        with open(TRAINING_LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        total += 1
                        if record.get("execution_success"):
                            success_count += 1
                        if record.get("user_satisfaction") is not None:
                            satisfaction_scores.append(record["user_satisfaction"])
                    except json.JSONDecodeError:
                        continue
        
        avg_satisfaction = (
            sum(satisfaction_scores) / len(satisfaction_scores)
            if satisfaction_scores
            else None
        )
        
        return {
            "total_logs": total,
            "success_rate": (success_count / total * 100) if total > 0 else 0.0,
            "avg_satisfaction": round(avg_satisfaction, 2) if avg_satisfaction else None,
            "satisfaction_count": len(satisfaction_scores),
            "file_path": str(TRAINING_LOG_FILE),
        }
    
    except Exception as e:
        logger.error(f"통계 조회 실패: {e}")
        return {"error": str(e)}


def export_training_dataset(
    output_format: str = "jsonl",
    success_only: bool = False,
    with_satisfaction_only: bool = False,
) -> Optional[str]:
    """
    훈련용 데이터셋 내보내기
    
    Args:
        output_format: 'jsonl' 또는 'json'
        success_only: 성공한 쿼리만 포함
        with_satisfaction_only: 사용자 평가가 있는 것만 포함
    
    Returns:
        str: 내보낸 파일 경로, 실패시 None
    """
    try:
        if not TRAINING_LOG_FILE.exists():
            logger.warning("훈련 데이터가 없습니다")
            return None
        
        records = []
        with open(TRAINING_LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        
                        if success_only and not record.get("execution_success"):
                            continue
                        if with_satisfaction_only and record.get("user_satisfaction") is None:
                            continue
                        
                        records.append(record)
                    except json.JSONDecodeError:
                        continue
        
        # 내보내기
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_format == "json":
            export_file = LOGS_DIR / f"training_dataset_{timestamp}.json"
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        else:  # jsonl
            export_file = LOGS_DIR / f"training_dataset_{timestamp}.jsonl"
            with open(export_file, "w", encoding="utf-8") as f:
                for record in records:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        logger.info(f"✅ 데이터셋 내보내기: {export_file}")
        return str(export_file)
    
    except Exception as e:
        logger.error(f"데이터셋 내보내기 실패: {e}")
        return None
