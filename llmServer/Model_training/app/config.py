#app/config.py
"""
[CONFIG] 환경설정 로더 (Chroma/RAG)

- .env를 로드하고
- Chroma / Retrieval 파라미터를 Settings로 제공한다.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def _to_int(value: Optional[str], default: int) -> int:
    if value is None or str(value).strip() == "":
        return default
    return int(str(value).strip())


def _to_float(value: Optional[str], default: float) -> float:
    if value is None or str(value).strip() == "":
        return default
    return float(str(value).strip())


@dataclass(frozen=True)
class Settings:
    chroma_path: Path
    chroma_collection: str
    top_k: int
    similarity_threshold: float
    debug: bool


def load_settings(env_path: Optional[str] = None) -> Settings:
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    chroma_path_raw = os.getenv("CHROMA_PATH", "").strip()
    if not chroma_path_raw:
        raise ValueError("CHROMA_PATH가 비어있습니다. .env에 CHROMA_PATH를 설정하세요.")

    chroma_collection = os.getenv("CHROMA_COLLECTION", "sql_templates").strip() or "sql_templates"
    top_k = _to_int(os.getenv("TOP_K"), 5)
    similarity_threshold = _to_float(os.getenv("SIMILARITY_THRESHOLD"), 0.0)

    debug_raw = os.getenv("DEBUG", "").strip().lower()
    debug = debug_raw in ("1", "true", "yes", "y", "on")

    chroma_path = Path(chroma_path_raw).expanduser().resolve()

    return Settings(
        chroma_path=chroma_path,
        chroma_collection=chroma_collection,
        top_k=top_k,
        similarity_threshold=similarity_threshold,
        debug=debug,
    )
