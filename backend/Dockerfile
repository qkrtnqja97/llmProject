FROM python:3.10-slim

# 로그 바로 출력
ENV PYTHONUNBUFFERED=1

WORKDIR /backendWorkspace

# 의존성 먼저 복사 (캐시 효율)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# backend 전체 복사
COPY . .

EXPOSE 8000

# 이건 stage나 dev나 어떤 환경에서든 들어갈 명령어니까 프로세스는 재시작 안할래. compose에서 override할래.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]  