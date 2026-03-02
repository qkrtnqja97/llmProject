#시작전 해당 코드 실행

conda create -n model_training python=3.10 -y
conda activate model_training
python -m pip install --upgrade pip
pip install -r requirements.txt


## ⚠ DB 접속 정보 (임시 설정)

현재 개발 단계에서는 `schema_tools/db_config.py`에
PostgreSQL DSN을 하드코딩하여 사용합니다.

예:
DB_DSN = "postgresql://postgres:password@127.0.0.1:5432/postgres"

### 📌 추후 개선 예정
- .env 파일 기반 환경변수 분리
- 운영/배포 환경에서는 반드시 하드코딩 제거
- 보안 강화를 위해 dotenv 또는 Secret Manager 적용 예정
