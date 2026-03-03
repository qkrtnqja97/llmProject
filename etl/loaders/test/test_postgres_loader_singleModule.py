# etl/loaders/postgres_loader_safe.py

import subprocess
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def open_tunnel(cloudflared_path: str, cloudflare_host: str, local_host: str, local_port: int, wait_sec: int = 5):
    """
    cloudflared 터널 열기
    """
    # 기존 터널 프로세스 종료
    subprocess.run(['pkill', '-f', 'cloudflared'], stderr=subprocess.DEVNULL)
    
    # 터널 커맨드
    tunnel_cmd = [
        cloudflared_path, 'access', 'tcp',
        '--hostname', cloudflare_host,
        '--url', f'tcp://{local_host}:{local_port}'
    ]
    proc = subprocess.Popen(tunnel_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f"cloudflare 연결 정보 tunnel_cmd : {tunnel_cmd}")
    time.sleep(wait_sec)
    print(f"✅ 터널 열림: {local_host}:{local_port} -> {cloudflare_host}")
    return proc

def connect_postgres(user: str, password: str, database: str, host: str='127.0.0.1', port: int=5432, timeout: int=10):
    """
    SQLAlchemy engine 생성 및 연결 확인
    """
    conn_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(conn_str, connect_args={'connect_timeout': timeout})
    
    # 연결 확인
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"연결완료 : engine - {engine}")
    except OperationalError as e:
        print(f"❌ DB 연결 실패: {e}")
        engine = None
    
    return engine

if __name__ == "__main__":
    # 예시 환경
    CLOUDFLARE_PATH = "/usr/local/bin/cloudflared"
    CLOUDFLARE_HOST = "dependence-dome-slideshow-mounted.trycloudflare.com"
    LOCAL_HOST, LOCAL_PORT = "127.0.0.1", 5432
    USER, PW, DB = "name", "1234", "postgres"

    print("터널링 시작 ...")
    proc = open_tunnel(CLOUDFLARE_PATH, CLOUDFLARE_HOST, LOCAL_HOST, LOCAL_PORT)

    print("DB 연결 시도 ...")
    engine = connect_postgres(USER, PW, DB, LOCAL_HOST, LOCAL_PORT)

    # 터널 종료
    proc.terminate()
    print("✅ 터널링 종료")