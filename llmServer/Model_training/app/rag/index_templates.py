#model_training/app/rag/index_templates.py
"""
[RAG] Template Indexer

📌 역할
- sql_templates_for_rag.jsonl 파일(문서 단위)을 읽어
- Chroma 컬렉션에 upsert(추가/갱신)
- (옵션) --reset 플래그가 켜지면 컬렉션을 초기화 후 재인덱싱

📦 입력 포맷(jsonl 각 줄)
{
  "pattern_id": "PAT_xxx",
  "sql_template": "...",
  "slots_schema": "...",
  "usage_count": 123,
  "example_question": "...",
  "text": "검색용 텍스트..."
}

📦 사용 라이브러리
- json: jsonl 파싱
- pathlib.Path: 파일 경로 처리
- argparse: CLI 옵션 처리(--jsonl, --reset)
- app.config: Settings
- app.rag.chroma_client: collection 획득
"""

from __future__ import annotations

import argparse  # ✅ 추가: CLI 옵션 처리
import json
from pathlib import Path
from typing import Dict, List, Tuple

import chromadb  # ✅ 추가: reset 시 client 직접 사용

from app.config import Settings, load_settings
from app.rag.chroma_client import get_or_create_collection


def _read_jsonl(path: Path) -> List[Dict]:
    """
    jsonl 파일을 읽어서 dict 리스트로 반환

    Args:
        path: jsonl 파일 경로

    Returns:
        list[dict]: 문서 목록
    """
    docs: List[Dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            docs.append(json.loads(line))
    return docs


def _reset_collection(settings: Settings) -> None:
    """
    ✅ Chroma 컬렉션 초기화(삭제 후 재생성)

    Args:
        settings: 환경설정 (chroma_path, chroma_collection 사용)
    """
    # Chroma Persistent client를 직접 생성해서 컬렉션을 삭제/재생성한다.
    client = chromadb.PersistentClient(path=str(settings.chroma_path))
    
    print(f"[RESET] collection 삭제 시도 중...: {settings.chroma_collection}")
    print(f"[RESET] Chroma 경로 : {settings.chroma_path}에서 삭제 시도 중...")

    deleted = False
    
    # delete_collection은 없을 수도 있으니 예외 안전 처리
    try:
        client.delete_collection(name=settings.chroma_collection)
        deleted = True
        print(f"[RESET] Collection 삭제됨: {settings.chroma_collection}")
    except Exception:
        # 컬렉션이 없거나 삭제 불가한 경우 무시하고 진행
        print(f"[RESET] Collection 검색실패 혹은 삭제 실패: {settings.chroma_collection}")

    # 재생성(이 시점에 빈 컬렉션 보장)
    client.get_or_create_collection(name=settings.chroma_collection)
    print(f"[RESET] Collection 재생성 완료")

    col = client.get_collection(name=settings.chroma_collection)
    print(f"[RESET] Collection 재생성 후 개수: {col.count()}")

def index_templates(settings: Settings, jsonl_path: str, reset: bool = False) -> Tuple[int, int]:
    """
    템플릿 jsonl을 Chroma에 업서트하는 함수

    Args:
        settings: 환경설정
        jsonl_path: sql_templates_for_rag.jsonl 경로
        reset: True면 컬렉션 초기화 후 인덱싱

    Returns:
        (upsert_count, total_docs): 업서트된 수, 전체 문서 수
    """
    path = Path(jsonl_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"템플릿 jsonl 파일이 없습니다: {path}")

    # ✅ reset 옵션 처리: 컬렉션 삭제 후 재생성
    if reset:
        _reset_collection(settings)

    _, collection = get_or_create_collection(settings)

    docs = _read_jsonl(path)

    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict] = []

    for d in docs:
        pattern_id = str(d.get("pattern_id", "")).strip()
        text = str(d.get("text", "")).strip()

        if not pattern_id or not text:
            # 필수 필드 없으면 스킵
            continue

        ids.append(pattern_id)
        documents.append(text)

        # metadata는 검색 결과로 다시 쓰기 좋게 최소 필드만 저장
        metadatas.append(
            {
                "pattern_id": pattern_id,
                "sql_template": d.get("sql_template", ""),
                "slots_schema": d.get("slots_schema", ""),
                "usage_count": int(d.get("usage_count", 0)),
                "example_question": d.get("example_question", ""),
            }
        )

    if not ids:
        return (0, len(docs))

    # upsert: id 동일하면 갱신
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    return (len(ids), len(docs))


if __name__ == "__main__":
    """
    실행 예:
    - 기본:
      python -m app.rag.index_templates

    - jsonl 경로 지정:
      python -m app.rag.index_templates --jsonl train_data/rag_templates/sql_templates_for_rag.jsonl

    - 컬렉션 초기화 후 재인덱싱:
      python -m app.rag.index_templates --reset
      python -m app.rag.index_templates --reset --jsonl train_data/rag_templates/sql_templates_for_rag.jsonl
    """
    settings = load_settings()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--jsonl",
        default=r"train_data\rag_templates\sql_templates_for_rag.jsonl",
        help="템플릿 jsonl 파일 경로",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Chroma 컬렉션을 삭제 후 재생성(초기화)한 뒤 인덱싱",
    )
    args = parser.parse_args()

    upserted, total = index_templates(settings, args.jsonl, reset=args.reset)

    print("✅ index done")
    print("Upserted :", upserted)
    print("Total    :", total)
    print("Reset    :", bool(args.reset))
    print("Collection:", settings.chroma_collection)
    print("ChromaPath:", settings.chroma_path)