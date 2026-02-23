# etl/loaders/test/test_chroma_loader.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from loaders.chroma_loader import get_chroma_client, get_collection


def test_connection():
    print("🔌 Chroma 연결 테스트 시작")

    client = get_chroma_client()

    try:
        client.heartbeat()
        print("✅ Chroma 서버 연결 성공")

        collections = client.list_collections()
        print(f"📦 현재 컬렉션 수: {len(collections)}")

        for col in collections:
            print(f" - {col.name}")

    except Exception as e:
        print(f"❌ Chroma 연결 실패: {e}")


def test_collection():
    print("\n📂 컬렉션 접근 테스트")

    try:
        col = get_collection("erp_collection")
        print(f"✅ 컬렉션 접근 성공: {col.name}")
        print(f"현재 데이터 수: {col.count()}")

    except Exception as e:
        print(f"❌ 컬렉션 접근 실패: {e}")


if __name__ == "__main__":
    test_connection()
    test_collection()