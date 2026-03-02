#a_db_config.py

"""
📌 역할:
- .env에서 DB 접속 설정을 읽어오는 "설정 모듈"
- 팀 표준(psycopg2)에 맞게 DB 접속 문자열(DSN)을 정규화(normalize)해서 제공

📦 사용 라이브러리:
- os: 환경 변수 접근
- dotenv(load_dotenv): .env 파일 로드

✅ 제공 값(다른 모듈에서 import해서 사용):
- DB_DSN: psycopg2가 이해할 수 있는 DSN 문자열 (예: postgresql://user:pw@host:port/db)
- DB_SCHEMA: 테이블 조회 시 사용할 스키마명 (예: inventory_mgmt)
"""

import os
from dotenv import load_dotenv

load_dotenv()

def _normalize_to_psycopg2_dsn(db_url: str) -> str:
    """
    DB_URL을 psycopg2에서 사용할 수 있는 DSN 형태로 정규화하는 함수

    psycopg2는 일반적으로:
      postgresql://user:password@host:port/dbname
    형태를 안정적으로 처리한다.

    반면 .env에 있는:
      postgresql+psycopg2://...
    는 SQLAlchemy 전용 URL 스킴이므로 그대로 psycopg2에 넣으면 실패한다.

    Args:
        db_url (str): .env에서 읽은 DB_URL

    Returns:
        str: psycopg2 호환 DSN 문자열
    """
    if not db_url:
        raise ValueError("DB_URL이 비어있습니다. .env에 DB_URL을 설정하세요.")

    # SQLAlchemy 전용 스킴을 psycopg2 호환 스킴으로 변환
    # 예) postgresql+psycopg2://user:pw@host:port/db -> postgresql://user:pw@host:port/db
    normalized = db_url.replace("postgresql+psycopg2://", "postgresql://", 1)

    # 혹시 mysql+pymysql 같은 다른 스킴이 들어온 경우를 빠르게 감지(안전장치)
    if "+psycopg2" in normalized:
        # 예상 외 케이스: replace가 안 된 경우
        normalized = normalized.replace("+psycopg2", "")

    return normalized

def _parse_search_path(raw: str) -> str:
    if not raw:
        return ""
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return ",".join(parts)


# -----------------------------
# .env 로드 및 설정 값 읽기
# -----------------------------

# .env에 이미 존재하는 키를 그대로 사용한다:
# DB_URL=postgresql+psycopg2://windowadmin6:1234@127.0.0.1:15435/postgres
_RAW_DB_URL = os.getenv("DB_URL", "").strip()

# psycopg2 연결에 사용할 DSN (정규화된 형태)
DB_DSN = _normalize_to_psycopg2_dsn(_RAW_DB_URL)
print("[db_config] DB_DSN =", DB_DSN)

# DB_SCHEMA=inventory_mgmt  (public이 아닌 별도 스키마면 반드시 필요)
DB_SCHEMA = os.getenv("DB_SCHEMA", "public").strip() or "public"

# ---- 복수 스키마 search_path ----
DB_SEARCH_PATH = _parse_search_path(os.getenv("DB_SEARCH_PATH", "").strip())
if not DB_SEARCH_PATH:
    DB_SEARCH_PATH = DB_SCHEMA

if __name__ == "__main__":
    # ✅ 단독 실행 시 설정값 프리뷰(디버깅용)
    # 비밀번호 노출 위험이 있으니 로컬에서만 확인하고 공유/커밋 금지
    print("DB_SCHEMA      =", DB_SCHEMA)
    print("DB_SEARCH_PATH =", DB_SEARCH_PATH)
    print("DB_DSN         =", DB_DSN)