# etl/loaders/test/test_postgres_loader.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2])) 
print(sys.path)

from loaders.postgres_loader import connect_postgres, load_table

if __name__ == "__main__":
    engine, proc = connect_postgres()
    try:
        # 1️⃣ 테이블 로드 테스트
        products = load_table(engine, "products")
        print(f"✅ [테스트] products 테이블 데이터 수: {len(products)}")
        print("샘플 데이터:", products[:2])  # 상위 2개 출력

    finally:
        # 2️⃣ 터널 종료
        proc.terminate()
        print("✅ 터널링 종료")