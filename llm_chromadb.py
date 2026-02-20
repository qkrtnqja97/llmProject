# llm_chromadb.py

import chromadb

CHROMA_TUNNEL_URL = "angle-temporal-absence-disks.trycloudflare.com"



def view_collection_by_table(target_table="products"):
    """특정 테이블 메타데이터를 가진 행만 필터링 조회"""
    client = chromadb.HttpClient(host=CHROMA_TUNNEL_URL, port=443, ssl=True)
    collection = client.get_collection(name="jw_gemini_collection")
    
    print(f"\n📂 [ChromaDB 필터링] {target_table} 데이터 조회 중...")
    
    # where 절을 사용하여 메타데이터 필터링
    results = collection.get(
        where={"table": target_table},
        limit=5,
        include=['documents', 'metadatas']
    )
    
    if not results['ids']:
        print(f"ℹ️ {target_table} 관련 데이터가 아직 없습니다.")
    for i in range(len(results['ids'])):
        print(f"[{i+1}] {results['documents'][i]}")
        print(f"   🏷️ {results['metadatas'][i]}")

if __name__ == "__main__":
    # "products", "current_products" 등 원하는 테이블명으로 교체하며 확인
    view_collection_by_table("products")