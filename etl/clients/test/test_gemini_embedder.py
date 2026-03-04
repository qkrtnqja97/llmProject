# etl/clients/test/test_gemini_embedder.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from clients.gemini_embedder import GeminiEmbedder


if __name__ == "__main__":
    print("🔌 Gemini Embedder 테스트 시작")

    try:
        embedder = GeminiEmbedder()

        texts = [
            "재고 관리 시스템입니다.",
            "ERP 기반 데이터 분석"
        ]

        vectors = embedder.embed(texts)

        print("✅ 임베딩 생성 성공")
        print("벡터 개수:", len(vectors))
        print("벡터 차원:", len(vectors[0]))

    except Exception as e:
        print("❌ 테스트 실패:", e)