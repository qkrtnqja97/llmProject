# -*- coding: utf-8 -*-
"""
엔티티 데이터 (manufacturers, vendors)
- PostgreSQL에서 동적으로 로드
- rag_builder에서 다른 컬렉션과 함께 단일 모델로 임베딩
"""

import sys
from pathlib import Path
from typing import List, Dict

# 경로 설정
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sqlalchemy import text
from api_llm.config import DATABASE_CONFIG
from api_llm.sql import get_database_manager


def get_entities_from_db() -> List[Dict]:
    """
    PostgreSQL에서 manufacturers, vendors 테이블의 모든 이름을 조회
    
    Returns:
        [
            {"name": "삼성전자", "type": "manufacturer"},
            {"name": "LG전자", "type": "manufacturer"},
            {"name": "고객A", "type": "vendor"},
            ...
        ]
    """
    try:
        db_manager = get_database_manager()
        engine = db_manager.get_engine()
        schema = DATABASE_CONFIG.get("SCHEMA", "public")
        
        entities = []
        
        with engine.connect() as conn:
            # ─── Manufacturers 조회 ───
            m_query = f"""
                SELECT DISTINCT name 
                FROM {schema}.manufacturers 
                WHERE name IS NOT NULL 
                ORDER BY name
            """
            m_rows = conn.execute(text(m_query)).fetchall()
            for row in m_rows:
                if row[0].strip():
                    entities.append({
                        "name": row[0],
                        "type": "manufacturer",
                    })
            
            # ─── Vendors 조회 ───
            v_query = f"""
                SELECT DISTINCT vendor_name 
                FROM {schema}.vendors 
                WHERE vendor_name IS NOT NULL 
                ORDER BY vendor_name
            """
            v_rows = conn.execute(text(v_query)).fetchall()
            for row in v_rows:
                if row[0].strip():
                    entities.append({
                        "name": row[0],
                        "type": "vendor",
                    })
        
        return entities
    
    except Exception as e:
        print(f"⚠️  엔티티 조회 실패: {e}")
        return []


# 동적 로드 (rag_builder 진입 시)
ENTITY_DATA = get_entities_from_db()
