# llm_progresql.py

import subprocess
import time
import sys
from sqlalchemy import create_engine, text



# --- [설정 정보] ---
NEW_URL = "dependence-dome-slideshow-mounted.trycloudflare.com"
USER, PW, DB = "name", "1234", "postgres"
LOCAL_HOST, LOCAL_PORT = "127.0.0.1", "5433"
TARGET_SCHEMA = "inventory_mgmt"



def connect_postgres():
    """Step 1: DB 터널 개방 및 접속"""
    subprocess.run(['pkill', '-f', 'cloudflared'], stderr=subprocess.DEVNULL)
    tunnel_cmd = ['./cloudflared', 'access', 'tcp', '--hostname', NEW_URL, '--url', f'tcp://{LOCAL_HOST}:{LOCAL_PORT}']
    proc = subprocess.Popen(tunnel_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)
    
    conn_str = f"postgresql+psycopg2://{USER}:{PW}@{LOCAL_HOST}:{LOCAL_PORT}/{DB}"
    engine = create_engine(conn_str, connect_args={'connect_timeout': 5})
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ DB 접속 성공")
            return engine, proc
    except Exception as e:
        print(f"❌ 접속 실패: {e}"); proc.terminate(); sys.exit(1)



# --- [데이터 가공 함수 구역] ---
def get_products_data(db_engine):
    """[기본 마스터] products 테이블 데이터 가공"""
    query = text(f"SELECT * FROM {TARGET_SCHEMA}.products")
    with db_engine.connect() as conn:
        rows = conn.execute(query).fetchall()
    
    documents, metadatas, ids = [], [], []
    for row in rows:
        doc = f"제품번호 {row.part_number}는 {row.description} 카테고리에 속하며, 표준 매입가는 {row.std_unit_cost}원, 표준 판매가는 {row.std_selling_price}원입니다."
        documents.append(doc)
        metadatas.append({"table": "products"})
        ids.append(f"prod_{row.part_number}")
    return documents, metadatas, ids

def get_current_stock_data(db_engine):
    """[1순위] 실시간 재고: products + current_products 조인"""
    query = text(f"""
        SELECT p.part_number, p.description, c.current_quantity, c.last_updated
        FROM {TARGET_SCHEMA}.products p
        JOIN {TARGET_SCHEMA}.current_products c ON p.part_number = c.part_number
    """)
    with db_engine.connect() as conn:
        rows = conn.execute(query).fetchall()
    
    documents, metadatas, ids = [], [], []
    for row in rows:
        doc = f"제품 {row.part_number}({row.description})의 현재 실시간 재고는 {row.current_quantity}개이며, 마지막 업데이트 일자는 {row.last_updated}입니다."
        documents.append(doc)
        metadatas.append({"table": "current_products"})
        ids.append(f"curr_{row.part_number}")
    return documents, metadatas, ids

def get_initial_inventory_data(db_engine):
    """[2순위] 기초 재고: initial_inventory"""
    query = text(f"SELECT * FROM {TARGET_SCHEMA}.initial_inventory")
    with db_engine.connect() as conn:
        rows = conn.execute(query).fetchall()
    
    documents, metadatas, ids = [], [], []
    for row in rows:
        doc = f"제품 {row.part_number}는 {row.stock_date} 기준 초기 재고 {row.initial_quantity}개로 시작되었습니다."
        documents.append(doc)
        metadatas.append({"table": "initial_inventory"})
        ids.append(f"init_{row.part_number}")
    return documents, metadatas, ids

def get_purchase_orders_data(db_engine):
    """[3순위] 입고 이력: purchase_orders + manufacturers 조인"""
    query = text(f"""
        SELECT p.*, m.name as m_name
        FROM {TARGET_SCHEMA}.purchase_orders p
        JOIN {TARGET_SCHEMA}.manufacturers m ON p.manufacturer_id = m.manufacturer_id
    """)
    with db_engine.connect() as conn:
        rows = conn.execute(query).fetchall()
    
    documents, metadatas, ids = [], [], []
    for row in rows:
        doc = f"{row.purchase_date}에 공급처 {row.m_name}으로부터 제품 {row.part_number}가 {row.purchase_quantity}개 입고되었습니다. 실제 매입 단가는 {row.actual_unit_cost}원입니다."
        documents.append(doc)
        metadatas.append({"table": "purchase_orders"})
        ids.append(f"pur_{row.purchase_id}")
    return documents, metadatas, ids

def get_sales_orders_data(db_engine):
    """[4순위] 출고 이력: sales_orders + vendors 조인"""
    query = text(f"""
        SELECT s.*, v.vendor_name
        FROM {TARGET_SCHEMA}.sales_orders s
        JOIN {TARGET_SCHEMA}.vendors v ON s.vendor_id = v.vendor_id
    """)
    with db_engine.connect() as conn:
        rows = conn.execute(query).fetchall()
    
    documents, metadatas, ids = [], [], []
    for row in rows:
        doc = f"{row.sale_date}에 고객사 {row.vendor_name}에게 제품 {row.part_number}가 {row.sale_quantity}개 출고되었습니다. 실제 판매가는 {row.actual_selling_price}원입니다."
        documents.append(doc)
        metadatas.append({"table": "sales_orders"})
        ids.append(f"sale_{row.order_id}")
    return documents, metadatas, ids




# --- [조회 유틸리티] ---
def inspect_table_data(db_engine, table_name, custom_sql=None):
    """테이블 상세 조회 (주석을 참고하여 활용하세요)"""
    print(f"\n🔍 [데이터 조회] 대상: {table_name if not custom_sql else 'Custom SQL'}")
    sql = custom_sql if custom_sql else f"SELECT * FROM {TARGET_SCHEMA}.{table_name} LIMIT 5"
    
    try:
        with db_engine.connect() as conn:
            result = conn.execute(text(sql))
            print(f"🔹 컬럼명: {list(result.keys())}")
            for row in result.fetchall():
                print(f"   {row}")
    except Exception as e:
        print(f"❌ 조회 실패: {e}")



if __name__ == "__main__":
    engine, proc = connect_postgres()
    try:
        # 순서대로 조회가 잘 되는지 여기서 테스트 가능합니다.
        # 1. 실시간 재고 조회 테스트
        inspect_table_data(engine, "current_products")
        
        # 2. 입고 이력(조인 결과) 확인을 위한 커스텀 SQL 테스트
        # join_sql = f"SELECT p.*, m.name FROM {TARGET_SCHEMA}.purchase_orders p JOIN {TARGET_SCHEMA}.manufacturers m ON p.manufacturer_id = m.manufacturer_id LIMIT 3"
        # inspect_table_data(engine, "purchase_orders", custom_sql=join_sql)

    finally:
        proc.terminate()