#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PostgreSQL 대화 히스토리 스키마 설정
- 새 스키마 'conversation' 생성
- 테이블 생성 (Hot + Cold 저장소)
- 함수 & 뷰 생성
"""

import sys
import logging
import os
from pathlib import Path

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("❌ psycopg2 미설치: pip install psycopg2-binary")
    sys.exit(1)

# .env 로드
try:
    from dotenv import load_dotenv
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

# DB 설정 (환경변수에서 직접 읽음)
DATABASE_CONFIG = {
    "USER": os.getenv("DB_USER", "postgres"),
    "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
    "HOST": os.getenv("DB_HOST", "192.168.0.176"),  # 로컬 네트워크 IP
    "PORT": int(os.getenv("DB_PORT", "5432")),
    "DB_NAME": os.getenv("DB_NAME", "inventory_db"),
}

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

# ==========================================
# 스키마 설정 (임시)
# ==========================================
# 나중에 DB 담당자가 만든 실제 스키마 이름으로 변경하면 됨
SCHEMA_NAME = "conversation"  # ← 임시 이름 (나중에 변경 가능)

print(f"📡 PostgreSQL 연결 정보 & 스키마:")
print(f"  - HOST: {DATABASE_CONFIG['HOST']}")
print(f"  - PORT: {DATABASE_CONFIG['PORT']}")
print(f"  - USER: {DATABASE_CONFIG['USER']}")
print(f"  - DB: {DATABASE_CONFIG['DB_NAME']}")
print(f"  - SCHEMA: {SCHEMA_NAME}")
print()


class ConversationSchemaSetup:
    """PostgreSQL 대화 스키마 설정"""
    
    def __init__(self):
        self.db_params = {
            "host": DATABASE_CONFIG["HOST"],
            "port": DATABASE_CONFIG["PORT"],
            "database": DATABASE_CONFIG["DB_NAME"],
            "user": DATABASE_CONFIG["USER"],
            "password": DATABASE_CONFIG["PASSWORD"],
        }
        self.conn = None
    
    def connect(self):
        """DB 연결"""
        try:
            self.conn = psycopg2.connect(**self.db_params)
            logger.info(f"✅ PostgreSQL 연결 성공: {self.db_params['host']}:{self.db_params['port']}/{self.db_params['database']}")
            return True
        except Exception as e:
            logger.error(f"❌ DB 연결 실패: {e}")
            return False
    
    def disconnect(self):
        """DB 연결 종료"""
        if self.conn:
            self.conn.close()
            logger.info("DB 연결 종료")
    
    def execute(self, query: str, fetch=False):
        """SQL 실행"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.conn.commit()
                cursor.close()
                return True
        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ SQL 실행 오류: {e}")
            logger.error(f"Query: {query[:200]}...")
            return False
    
    def create_schema(self):
        """스키마 생성 (이미 존재한다고 가정)"""
        logger.info("\n[1/3] 스키마 확인...")
        query = f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{SCHEMA_NAME}';"
        result = self.execute(query, fetch=True)
        if result:
            logger.info(f"✅ 스키마 '{SCHEMA_NAME}' 확인 완료 (이미 존재)")
            return True
        else:
            logger.warning(f"⚠️ 스키마 '{SCHEMA_NAME}' 확인 안 됨 - DB 담당자가 생성해주세요")
            return False
    
    def create_tables(self):
        """테이블 생성 (2개)"""
        logger.info("\n[2/3] 테이블 생성...")
        
        # 1. conversation_history (Hot - 1개월)
        query1 = f"""
        CREATE TABLE {SCHEMA_NAME}.conversation_history (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) DEFAULT 'anonymous',
            
            -- 입력 데이터
            question TEXT NOT NULL,
            refined_question TEXT,
            
            -- 응답 데이터
            response_data JSONB,
            sql_query TEXT,
            execution_time_ms FLOAT,
            
            -- 메타데이터
            entity_corrections JSONB,
            validation_result VARCHAR(50),
            error_message TEXT,
            
            -- 타임스탐프 & 보관 정책
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            is_archived BOOLEAN DEFAULT FALSE,
            
            CONSTRAINT expires_at_after_created CHECK (expires_at > created_at)
        );
        
        CREATE INDEX idx_conversation_history_expires_at 
            ON {SCHEMA_NAME}.conversation_history(expires_at) 
            WHERE is_archived = FALSE;
        CREATE INDEX idx_conversation_history_created_at 
            ON {SCHEMA_NAME}.conversation_history(created_at DESC);
        CREATE INDEX idx_conversation_history_user_id 
            ON {SCHEMA_NAME}.conversation_history(user_id);
        """
        
        if not self.execute(query1):
            return False
        logger.info("  ✅ conversation_history 테이블 생성")
        
        # 2. conversation_archive (Cold - 6개월+)
        query2 = f"""
        CREATE TABLE {SCHEMA_NAME}.conversation_archive (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) DEFAULT 'anonymous',
            
            -- 입력 데이터
            question TEXT NOT NULL,
            refined_question TEXT,
            
            -- 응답 데이터
            response_data JSONB,
            sql_query TEXT,
            execution_time_ms FLOAT,
            
            -- 메타데이터
            entity_corrections JSONB,
            validation_result VARCHAR(50),
            error_message TEXT,
            
            -- 타임스탐프 & 보관 정책
            created_at TIMESTAMP,
            archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            
            -- 학습용 메타데이터
            is_training_data BOOLEAN DEFAULT FALSE,
            training_batch_id VARCHAR(255),
            
            CONSTRAINT archive_expires_after_created CHECK (expires_at > created_at)
        );
        
        CREATE INDEX idx_conversation_archive_archived_at 
            ON {SCHEMA_NAME}.conversation_archive(archived_at DESC);
        CREATE INDEX idx_conversation_archive_created_at 
            ON {SCHEMA_NAME}.conversation_archive(created_at);
        CREATE INDEX idx_conversation_archive_training_batch 
            ON {SCHEMA_NAME}.conversation_archive(training_batch_id);
        CREATE INDEX idx_conversation_archive_is_training 
            ON {SCHEMA_NAME}.conversation_archive(is_training_data);
        """
        
        if not self.execute(query2):
            return False
        logger.info("  ✅ conversation_archive 테이블 생성")
        
        return True
    
    def create_functions(self):
        """함수 생성"""
        logger.info("\n[3/3] 함수 생성...")
        
        # 1. archive_expired_conversations()
        query1 = f"""
        CREATE OR REPLACE FUNCTION {SCHEMA_NAME}.archive_expired_conversations()
        RETURNS TABLE(archived_count INT, message VARCHAR) AS $$
        DECLARE
            count_archived INT;
        BEGIN
            -- 1. 1개월 이상 지난 데이터를 archive로 이동
            INSERT INTO {SCHEMA_NAME}.conversation_archive (
                user_id, question, refined_question, response_data, sql_query,
                execution_time_ms, entity_corrections, validation_result, error_message,
                created_at, expires_at
            )
            SELECT 
                user_id, question, refined_question, response_data, sql_query,
                execution_time_ms, entity_corrections, validation_result, error_message,
                created_at, (created_at + INTERVAL '6 months')
            FROM {SCHEMA_NAME}.conversation_history
            WHERE created_at < NOW() - INTERVAL '1 month'
            AND is_archived = FALSE;
            
            GET DIAGNOSTICS count_archived = ROW_COUNT;
            
            -- 2. 아카이빙 완료된 데이터 삭제
            DELETE FROM {SCHEMA_NAME}.conversation_history
            WHERE created_at < NOW() - INTERVAL '1 month'
            AND is_archived = FALSE;
            
            RETURN QUERY SELECT count_archived::INT, 
                ('Successfully archived ' || count_archived || ' conversations')::VARCHAR;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        if not self.execute(query1):
            return False
        logger.info("  ✅ archive_expired_conversations() 함수 생성")
        
        return True
    
    def create_views(self):
        """뷰 생성"""
        logger.info("\n[3/3] 뷰 생성...")
        
        query = f"""
        CREATE OR REPLACE VIEW {SCHEMA_NAME}.conversation_training_data AS
        SELECT 
            id,
            user_id,
            question,
            refined_question,
            sql_query,
            (response_data->>'result_summary') AS result_summary,
            validation_result,
            execution_time_ms,
            created_at
        FROM {SCHEMA_NAME}.conversation_archive
        WHERE is_training_data = TRUE
        AND created_at >= CURRENT_DATE - INTERVAL '6 months'
        ORDER BY created_at DESC;
        """
        
        if not self.execute(query):
            return False
        logger.info("  ✅ conversation_training_data 뷰 생성")
        
        return True
    
    def verify_schema(self):
        """스키마 검증"""
        logger.info("\n[✓] 스키마 검증...")
        
        query = f"""
        SELECT 
            (SELECT COUNT(*) FROM information_schema.tables 
             WHERE table_schema = '{SCHEMA_NAME}') as table_count,
            (SELECT COUNT(*) FROM information_schema.routines 
             WHERE routine_schema = '{SCHEMA_NAME}' AND routine_type = 'FUNCTION') as function_count,
            (SELECT COUNT(*) FROM information_schema.views 
             WHERE table_schema = '{SCHEMA_NAME}') as view_count;
        """
        
        result = self.execute(query, fetch=True)
        if result:
            row = result[0]
            tables = row[0]
            functions = row[1]
            views = row[2]
            logger.info(f"  📊 테이블: {tables}개, 함수: {functions}개, 뷰: {views}개")
            return tables >= 2
        
        return False
    
    def setup(self):
        """전체 설정 실행"""
        if not self.connect():
            return False
        
        try:
            steps = [
                ("스키마 생성", self.create_schema),
                ("테이블 생성", self.create_tables),
                ("함수 생성", self.create_functions),
                ("뷰 생성", self.create_views),
                ("스키마 검증", self.verify_schema),
            ]
            
            for step_name, step_func in steps:
                if not step_func():
                    logger.error(f"❌ {step_name} 실패")
                    return False
            
            logger.info("\n" + "="*60)
            logger.info("✅ PostgreSQL 대화 히스토리 스키마 설정 완료!")
            logger.info("="*60)
            return True
        
        finally:
            self.disconnect()


if __name__ == "__main__":
    setup = ConversationSchemaSetup()
    success = setup.setup()
    sys.exit(0 if success else 1)
