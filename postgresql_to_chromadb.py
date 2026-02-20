# postgresql_to_chromadb.py

import time
import chromadb
from llm_postgresql import (
    connect_postgres, 
    get_products_data,
    get_current_stock_data,
    get_initial_inventory_data,
    get_purchase_orders_data,
    get_sales_orders_data
)
from embed import get_embeddings_batch



def sync_to_server():
    print("\n--- 🔄 데이터 동기화 프로세스 시작 ---")
    
    # [Step 1] 인프라 연결
    db_engine, tunnel_proc = connect_postgres()
    
    try:
        # [Step 2] ChromaDB 접속 및 설정
        CHROMA_TUNNEL_URL = "angle-temporal-absence-disks.trycloudflare.com"
        client = chromadb.HttpClient(host=CHROMA_TUNNEL_URL, port=443, ssl=True)
        collection = client.get_or_create_collection(name="jw_gemini_collection")
        
        # [중요] 임베딩할 테이블을 여기서 하나만 선택하세요! (나머지는 주석 처리)
        # ---------------------------------------------------------------------
        print("🚀 [Step 3] Postgres에서 데이터를 추출하는 중...")
        
        # documents, metadatas, ids = get_products_data(db_engine)             # (기본) 제품 마스터
        # documents, metadatas, ids = get_current_stock_data(db_engine)        # (1순위) 실시간 재고
        documents, metadatas, ids = get_initial_inventory_data(db_engine)      # (2순위) 기초 재고
        # documents, metadatas, ids = get_purchase_orders_data(db_engine)      # (3순위) 입고 이력
        # documents, metadatas, ids = get_sales_orders_data(db_engine)         # (4순위) 출고 이력
        # ---------------------------------------------------------------------

        # [Step 4] 중복 저장 확인 및 제외 (Skip 로직)
        print("🚀 [Step 4] 기존 저장 데이터 확인 중...")
        existing_ids = set(collection.get()['ids'])
        
        # 아직 DB에 없는 신규 인덱스만 추출
        new_indices = [idx for idx, val in enumerate(ids) if val not in existing_ids]
        
        final_docs = [documents[i] for i in new_indices]
        final_metas = [metadatas[i] for i in new_indices]
        final_ids = [ids[i] for i in new_indices]
        
        total_new = len(final_docs)
        if total_new == 0:
            print("   ✅ 모든 데이터가 이미 최신 상태입니다. (추가할 데이터 없음)")
            return

        print(f"📦 [진행] 총 {total_new}건의 신규 데이터를 처리합니다. (50개씩 전송)")

        # [Step 5] 배치 임베딩 및 저장 (할당량 보호)
        batch_size = 50  # 사용자님 설정값: 50개
        for i in range(0, total_new, batch_size):
            b_docs = final_docs[i : i + batch_size]
            b_metas = final_metas[i : i + batch_size]
            b_ids = final_ids[i : i + batch_size]
            
            # 임베딩 생성 (embeddings 변수명 사용)
            embeddings = get_embeddings_batch(b_docs)
            
            if embeddings:
                collection.add(
                    embeddings=embeddings,
                    documents=b_docs,
                    metadatas=b_metas,
                    ids=b_ids
                )
                current_count = i + len(b_docs)
                print(f"   ✅ [{current_count}/{total_new}] 완료 (61초 대기 중...)")
                time.sleep(61)
            else:
                print(f"   ⚠️ [{i}] 배치 임베딩 실패. 다음 실행 시 이어서 진행됩니다.")
                break # 실패 시 안전을 위해 중단

    except Exception as e:
        print(f"❌ 치명적 오류 발생: {e}")
    finally:
        if 'tunnel_proc' in locals():
            tunnel_proc.terminate()
            print("🏁 DB 터널링 세션을 닫고 안전하게 종료합니다.")



if __name__ == "__main__":
    sync_to_server()