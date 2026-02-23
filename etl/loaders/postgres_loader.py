# etl/loaders/postgres_loader.py

import subprocess
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from config.etl_config import POSTGRES_CONFIG, CLOUDFLARE_CONFIG

def open_tunnel(wait_sec: int = 5):
    """
    cloudflared 터널 열기
    """
    # 기존 터널 종료
    subprocess.run(['pkill', '-f', 'cloudflared'], stderr=subprocess.DEVNULL)

    tunnel_cmd = [
        '/usr/local/bin/cloudflared',
        'access', 'tcp',
        '--hostname', CLOUDFLARE_CONFIG['host'],
        '--url', f"tcp://{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}"
    ]
    proc = subprocess.Popen(tunnel_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f"cloudflare 연결 정보 tunnel_cmd : {tunnel_cmd}")
    time.sleep(wait_sec)
    print(f"✅ 터널 열림: {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']} -> {CLOUDFLARE_CONFIG['host']}")
    return proc

def connect_postgres(timeout: int = 10, wait_sec: int = 5):
    """
    터널 열기 + SQLAlchemy engine 생성 및 연결 확인
    """
    # 1️⃣ 터널 열기
    proc = open_tunnel(wait_sec=5)

    # 2️⃣ DB 연결
    conn_str = (
        f"postgresql+psycopg2://{POSTGRES_CONFIG['user']}:"
        f"{POSTGRES_CONFIG['password']}@{POSTGRES_CONFIG['host']}:"
        f"{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"
    )
    engine = create_engine(conn_str, connect_args={'connect_timeout': timeout})

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"✅ DB 연결 완료 : {engine}")
    except OperationalError as e:
        print(f"❌ DB 연결 실패: {e}")
        engine = None

    return engine, proc

def load_table(engine, table_name, custom_sql=None):
    query = custom_sql or f"SELECT * FROM {POSTGRES_CONFIG['schema']}.{table_name}"
    with engine.connect() as conn:
        return conn.execute(text(query)).fetchall()

