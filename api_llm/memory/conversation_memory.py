# -*- coding: utf-8 -*-
"""
대화 메모리 관리
- 질문-응답 쌍을 메모리에 저장 (세션 + DB)
- 유사한 질문 감지 후 캐시된 응답 반환
- Claude, ChatGPT 같은 대화 히스토리 기능 제공
- 1개월: Hot 데이터 (빠른 응답)
- 6개월+: Cold 데이터 (모델 파인튜닝용)
"""

import logging
import hashlib
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np

try:
    import psycopg2
    from psycopg2.extras import Json
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# config.py에서 DB 설정 import
try:
    from config import DATABASE_URL
    DB_URL_CONFIG = DATABASE_URL
except ImportError:
    DB_URL_CONFIG = None

logger = logging.getLogger(__name__)


# ==========================================
# DB Manager (PostgreSQL)
# ==========================================
class DBManager:
    """PostgreSQL 연결 관리"""
    
    def __init__(self, db_url: str, schema_name: str = "sql_assistant"):
        """
        Args:
            db_url: PostgreSQL 연결 문자열 (postgresql+psycopg2://user:pass@host:port/db)
            schema_name: 스키마 이름 (기본값: "sql_assistant")
        """
        self.db_url = db_url
        self.schema_name = schema_name  # ← "sql_assistant" (DB 담당자가 만든 스키마)
        self.conn = None
        self._parse_url()
    
    def _parse_url(self):
        """PostgreSQL URL 파싱"""
        # 형식: postgresql+psycopg2://user:password@host:port/dbname
        url = self.db_url.replace("postgresql+psycopg2://", "")
        creds, rest = url.split("@")
        user, password = creds.split(":")
        host_port, dbname = rest.split("/")
        host, port = host_port.split(":")
        
        self.db_params = {
            "host": host,
            "port": int(port),
            "database": dbname,
            "user": user,
            "password": password,
        }
    
    def connect(self):
        """DB 연결"""
        try:
            if not PSYCOPG2_AVAILABLE:
                logger.warning("⚠️ psycopg2 미설치: pip install psycopg2-binary")
                return False
            
            self.conn = psycopg2.connect(**self.db_params)
            logger.info("✅ PostgreSQL 연결 성공")
            return True
        except Exception as e:
            logger.error(f"❌ DB 연결 실패: {e}")
            return False
    
    def disconnect(self):
        """DB 연결 종료"""
        if self.conn:
            self.conn.close()
            logger.info("DB 연결 종료")
    
    def execute(self, query: str, params: tuple = None) -> List[Dict]:
        """SQL 쿼리 실행"""
        if not self.conn:
            return None
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith("SELECT"):
                columns = [desc[0] for desc in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                cursor.close()
                return results
            else:
                self.conn.commit()
                cursor.close()
                return True
        except Exception as e:
            logger.error(f"쿼리 실행 오류: {e}")
            if self.conn:
                self.conn.rollback()
            return None


# ==========================================
# ConversationMemory (Session + DB)
# ==========================================

class ConversationMemory:
    """대화 메모리 관리자 (세션 + DB)"""
    
    def __init__(
        self,
        max_entries: int = 100,
        similarity_threshold: float = 0.85,
        db_url: str = None,
        user_id: str = "anonymous"
    ):
        """
        Args:
            max_entries: 최대 저장 개수 (초과 시 FIFO 제거)
            similarity_threshold: 질문 유사도 기준 (0~1, 높을수록 엄격)
            db_url: PostgreSQL 연결 문자열 (선택사항)
            user_id: 사용자 ID
        """
        self.max_entries = max_entries
        self.similarity_threshold = similarity_threshold
        self.user_id = user_id
        self.conversations = []  # 메모리 (세션)
        self.embeddings_cache = {}  # 질문 임베딩 캐시
        
        # DB 연결 (선택사항)
        self.db_manager = None
        if db_url:
            self.db_manager = DBManager(db_url, schema_name="sql_assistant")  # ← 실제 스키마
            if self.db_manager.connect():
                logger.info(f"💾 DB 저장소 활성화 (사용자: {user_id}, 스키마: {self.db_manager.schema_name})")

        
    def add_conversation(
        self,
        question: str,
        response: Dict,
        metadata: Dict = None,
        save_to_db: bool = True
    ) -> None:
        """
        대화를 메모리 + DB에 저장
        
        Args:
            question: 사용자 질문
            response: 응답 결과 (차트 정보, 데이터, 답변 등)
            metadata: 추가 메타데이터 (실행 시간, SQL 등)
            save_to_db: DB에도 저장할지 여부
        """
        entry = {
            "id": len(self.conversations),
            "question": question,
            "response": response,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "hash": self._hash_question(question),
        }
        
        self.conversations.append(entry)
        
        # max_entries 초과 시 오래된 것 제거 (FIFO)
        if len(self.conversations) > self.max_entries:
            removed = self.conversations.pop(0)
            logger.info(f"🗑️ 메모리 초과 → 제거: {removed['question'][:50]}")
        
        # DB에 저장 (1개월 Hot 데이터)
        if save_to_db and self.db_manager:
            self._save_to_db_hot(entry)
        
        logger.info(f"💾 메모리 저장 | 총 {len(self.conversations)}개 (사용자: {self.user_id})")
    
    def _save_to_db_hot(self, entry: Dict) -> bool:
        """대화를 DB에 저장 (conversations + request_logs 테이블)"""
        if not self.db_manager:
            logger.warning(f"⚠️ DB 매니저 없음 (저장 스킵)")
            return False
        
        if not self.db_manager.conn:
            logger.warning(f"⚠️ DB 연결 없음 (저장 스킵)")
            return False
        
        try:
            now = datetime.now()
            sql_query = entry["metadata"].get("sql_query", None)
            execution_time = int(entry["metadata"].get("execution_time_ms", 0))
            entity_corrections = entry["metadata"].get("entity_corrections", {})
            validation_result = entry["metadata"].get("validation_result", "OK")
            refined_question = entry["metadata"].get("refined_question", entry["question"])
            error_msg = entry["metadata"].get("error_message", None)
            execution_success = entry["metadata"].get("execution_success", True)
            row_count = int(entry["metadata"].get("row_count", 0))
            
            schema = self.db_manager.schema_name
            logger.info(f"🔄 DB 저장 시작 (schema: {schema}, user: {self.user_id})")
            
            cursor = self.db_manager.conn.cursor()
            
            # JSON 인코딩
            response_json = json.dumps(
                entry["response"], 
                ensure_ascii=False, 
                default=str
            )
            entity_corrections_json = json.dumps(
                entity_corrections, 
                ensure_ascii=False
            )
            
            # 1. conversations 테이블에 저장
            try:
                query1 = f"""
                INSERT INTO {schema}.conversations (
                    user_id, session_id, role, question, refined_question, 
                    response_data, final_sql, entity_corrections, 
                    execution_time_ms, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING conv_id
                """
                
                cursor.execute(
                    query1,
                    (
                        self.user_id,
                        self.user_id,  # session_id = user_id (이미 UUID로 설정됨)
                        'user',  # role
                        entry["question"],
                        refined_question,
                        response_json,
                        sql_query,
                        entity_corrections_json,
                        execution_time,
                        now
                    )
                )
                
                result = cursor.fetchone()
                if result:
                    conv_id = result[0]
                    logger.info(f"✅ conversations 저장 (conv_id: {conv_id})")
                else:
                    logger.warning(f"⚠️ conversations INSERT 후 conv_id 미반환")
                    conv_id = None
                
            except Exception as e:
                logger.error(f"❌ conversations 테이블 저장 실패: {e}")
                logger.debug(f"   쿼리: {query1}")
                logger.debug(f"   파라미터: user_id={self.user_id}, question={entry['question'][:50]}")
                cursor.close()
                try:
                    self.db_manager.conn.rollback()
                except:
                    pass
                return False
            
            # 2. request_logs 테이블에도 저장 (추적용)
            try:
                query2 = f"""
                INSERT INTO {schema}.request_logs (
                    user_id, question, refined_question, entity_corrections,
                    final_sql, execution_success, execution_time_ms,
                    error_message, row_count, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(
                    query2,
                    (
                        self.user_id,
                        entry["question"],
                        refined_question,
                        entity_corrections_json,
                        sql_query,
                        execution_success,
                        execution_time,
                        error_msg,
                        row_count,
                        now
                    )
                )
                logger.info(f"✅ request_logs 저장 완료")
                
            except Exception as e:
                logger.error(f"❌ request_logs 테이블 저장 실패: {e}")
                logger.debug(f"   쿼리: {query2}")
                cursor.close()
                try:
                    self.db_manager.conn.rollback()
                except:
                    pass
                return False
            
            # 커밋
            try:
                self.db_manager.conn.commit()
                logger.info(f"✅ DB 커밋 성공 (사용자: {self.user_id})")
            except Exception as e:
                logger.error(f"❌ DB 커밋 실패: {e}")
                self.db_manager.conn.rollback()
                cursor.close()
                return False
            finally:
                cursor.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ DB Hot 저장 실패: {e}", exc_info=True)
            try:
                self.db_manager.conn.rollback()
            except:
                pass
            return False

    
    def find_similar_question(
        self,
        question: str,
        embedder=None
    ) -> Optional[Dict]:
        """
        유사한 과거 질문 찾기 (유사도 기반)
        
        Args:
            question: 검색할 질문
            embedder: sentence-transformers 모델 (None이면 문자열 기반 비교)
        
        Returns:
            유사한 대화 entry 또는 None
        """
        if not self.conversations:
            return None
        
        # 1단계: 정확한 질문 찾기 (빠름)
        question_hash = self._hash_question(question)
        for entry in self.conversations:
            if entry["hash"] == question_hash:
                logger.info(f"✅ 정확한 질문 매칭 | '{question[:50]}'")
                return entry
        
        # 2단계: 유사도 기반 검색 (임베딩 사용)
        if embedder is None:
            return None
        
        try:
            # 현재 질문 임베딩
            q_embedding = embedder.encode([question], show_progress_bar=False)[0]
            q_embedding = np.array(q_embedding, dtype=np.float32)
            
            best_match = None
            best_score = 0
            
            for entry in self.conversations:
                entry_hash = entry["hash"]
                
                # 캐시된 임베딩 사용
                if entry_hash in self.embeddings_cache:
                    cached_embedding = self.embeddings_cache[entry_hash]
                else:
                    # 새로 생성 및 캐시
                    cached_embedding = embedder.encode(
                        [entry["question"]], 
                        show_progress_bar=False
                    )[0]
                    cached_embedding = np.array(cached_embedding, dtype=np.float32)
                    self.embeddings_cache[entry_hash] = cached_embedding
                
                # 코사인 유사도 계산
                from sklearn.metrics.pairwise import cosine_similarity
                similarity = cosine_similarity(
                    [q_embedding],
                    [cached_embedding]
                )[0][0]
                
                if similarity > best_score and similarity >= self.similarity_threshold:
                    best_score = similarity
                    best_match = entry
            
            if best_match:
                logger.info(
                    f"🔍 유사 질문 발견 ({best_score:.2%}) | "
                    f"'{best_match['question'][:50]}'"
                )
                return best_match
        
        except Exception as e:
            logger.warning(f"⚠️ 유사도 검색 실패: {e}")
        
        return None
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """
        대화 히스토리 조회
        
        Args:
            limit: 최근 N개 조회
        
        Returns:
            대화 목록 (최신순)
        """
        return list(reversed(self.conversations[-limit:]))
    
    def clear(self) -> None:
        """메모리 전체 삭제"""
        self.conversations = []
        self.embeddings_cache = {}
        logger.info("🗑️ 메모리 전체 삭제")
    
    # ==========================================
    # DB 네트워크 관련 메서드
    # ==========================================
    
    def archive_expired_conversations(self) -> Dict:
        """
        1개월 이상 지난 대화를 archive 테이블로 이동
        (DB의 archive_expired_conversations() 함수 호출)
        
        Returns:
            아카이빙 결과 {'archived_count': int, 'message': str}
        """
        if not self.db_manager or not self.db_manager.conn:
            logger.warning("⚠️ DB 연결 없음: 아카이빙 불가")
            return {"archived_count": 0, "message": "DB not connected"}
        
        try:
            result = self.db_manager.execute(f"SELECT {self.db_manager.schema_name}.archive_expired_conversations();")
            if result and len(result) > 0:
                archived = result[0].get("archive_expired_conversations", (0, "Failed"))
                if isinstance(archived, tuple):
                    count, msg = archived
                else:
                    count, msg = 0, str(archived)
                logger.info(f"✅ 아카이빙 완료: {count}개 대화")
                return {"archived_count": count, "message": msg}
        except Exception as e:
            logger.error(f"❌ 아카이빙 실패: {e}")
        
        return {"archived_count": 0, "message": "Archiving failed"}
    
    def get_db_stats(self) -> Dict:
        """DB 상의 대화 통계 (사용자별 격리)"""
        if not self.db_manager or not self.db_manager.conn:
            return {
                "active_conversations": 0,
                "total_requests": 0,
                "avg_execution_time": 0,
            }
        
        try:
            # conversations 테이블에서 통계 조회
            query = f"""
            SELECT 
                (SELECT COUNT(*) FROM {self.db_manager.schema_name}.conversations 
                 WHERE is_archived = FALSE AND user_id = %s) as active_count,
                (SELECT COUNT(*) FROM {self.db_manager.schema_name}.request_logs 
                 WHERE user_id = %s) as request_count,
                (SELECT COALESCE(AVG(execution_time_ms), 0) FROM {self.db_manager.schema_name}.request_logs 
                 WHERE user_id = %s) as avg_time
            """
            result = self.db_manager.execute(query, (self.user_id, self.user_id, self.user_id))
            if result:
                row = result[0]
                return {
                    "active_conversations": row.get("active_count", 0),
                    "total_requests": row.get("request_count", 0),
                    "avg_execution_time": round(row.get("avg_time", 0), 2),
                }
        except Exception as e:
            logger.warning(f"⚠️ DB 통계 조회 실패: {e}")
        
        return {
            "active_conversations": 0,
            "total_requests": 0,
            "avg_execution_time": 0,
        }
    
    def export_training_data(self, filepath: str) -> bool:
        """
        학습용 데이터를 JSON으로 내보내기 (사용자별 격리)
        conversations 테이블에서 추출
        
        Args:
            filepath: 저장할 파일 경로
        
        Returns:
            성공 여부
        """
        if not self.db_manager or not self.db_manager.conn:
            logger.warning("⚠️ DB 연결 없음: 내보내기 불가")
            return False
        
        try:
            query = f"""
            SELECT 
                question, refined_question, final_sql as sql_query,
                validation_result, execution_time_ms,
                created_at
            FROM {self.db_manager.schema_name}.conversations
            WHERE user_id = %s
            ORDER BY created_at DESC
            """
            
            result = self.db_manager.execute(query, (self.user_id,))
            if result:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"✅ 학습 데이터 내보내기 완료: {filepath} ({len(result)}개 레코드, 사용자: {self.user_id})")
                return True
        except Exception as e:
            logger.error(f"❌ 학습 데이터 내보내기 실패: {e}")
        
        return False
    
    def load_recent_from_db(self, limit: int = 20) -> List[Dict]:
        """DB에서 최근 대화 로드 (사용자별 격리)"""
        if not self.db_manager or not self.db_manager.conn:
            return []
        
        try:
            query = f"""
            SELECT 
                conv_id as id, user_id, question, refined_question, response_data,
                final_sql as sql_query, execution_time_ms, created_at
            FROM {self.db_manager.schema_name}.conversations
            WHERE is_archived = FALSE AND user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """
            
            result = self.db_manager.execute(query, (self.user_id, limit))
            logger.info(f"✅ DB conversations에서 {len(result or [])}개 대화 로드 (사용자: {self.user_id})")
            return result or []
        except Exception as e:
            logger.warning(f"⚠️ conversations 테이블 로드 실패: {e}")
        
        return []

    
    def get_stats(self) -> Dict:
        """메모리 + DB 통계"""
        stats = {
            # 메모리 통계
            "memory": {
                "total_conversations": len(self.conversations),
                "max_entries": self.max_entries,
                "cached_embeddings": len(self.embeddings_cache),
                "memory_usage_mb": self._estimate_memory_mb(),
            },
            # DB 통계
            "database": self.get_db_stats(),
        }
        return stats
    
    @staticmethod
    def _hash_question(question: str) -> str:
        """질문의 정규화된 해시 생성"""
        normalized = question.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _estimate_memory_mb(self) -> float:
        """메모리 사용량 추정 (MB)"""
        import sys
        total_size = sys.getsizeof(self.conversations)
        total_size += sys.getsizeof(self.embeddings_cache)
        
        # 각 entry의 크기 계산 (JSON 직렬화 불가능한 객체 처리)
        for entry in self.conversations:
            try:
                # JSON 직렬화 시도
                total_size += sys.getsizeof(json.dumps(entry))
            except (TypeError, ValueError):
                # 직렬화 불가능한 경우 각 항목의 크기만 계산
                total_size += sys.getsizeof(entry.get("timestamp", ""))
                total_size += sys.getsizeof(entry.get("question", ""))
                total_size += sys.getsizeof(entry.get("hash", ""))
                total_size += sys.getsizeof(entry.get("metadata", {}))
                
                # response 객체는 복잡할 수 있으므로 기본 크기만 계산
                if "response" in entry:
                    try:
                        total_size += sys.getsizeof(entry["response"])
                    except:
                        total_size += 1024  # 기본값 ~1KB
        
        # numpy array 크기 계산
        for embedding in self.embeddings_cache.values():
            if hasattr(embedding, 'nbytes'):
                total_size += embedding.nbytes
            else:
                total_size += sys.getsizeof(embedding)
        
        return round(total_size / (1024 * 1024), 2)
    
    def export_to_json(self, filepath: str) -> None:
        """대화 히스토리를 JSON으로 내보내기"""
        try:
            export_data = []
            for entry in self.conversations:
                export_entry = {
                    "timestamp": entry["timestamp"],
                    "question": entry["question"],
                    "response_keys": list(entry["response"].keys()),
                    "metadata": entry["metadata"],
                }
                export_data.append(export_entry)
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ 메모리 내보내기 완료: {filepath}")
        except Exception as e:
            logger.warning(f"내보내기 실패: {e}")
