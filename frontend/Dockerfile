FROM node:20-slim

# 1. 작업 디렉토리 설정 (백엔드와 통일감 있게 설정)
WORKDIR /frontendWorkspace

# 2. 의존성 파일 복사 (캐시 효율 극대화)
COPY package.json package-lock.json* ./

# 3. 패키지 설치
# 빌드 속도를 위해 개발 의존성(devDependencies)까지 모두 설치합니다.
RUN npm install

# 4. 소스 코드 전체 복사
COPY . .

# 5. Vite 기본 포트 노출
EXPOSE 5173

# 6. 실행 명령어
# Vite 7은 기본적으로 로컬호스트만 허용하므로 --host 0.0.0.0 설정이 필수입니다.
# 백엔드처럼 compose에서 커스텀할 수 있도록 기본 프로세스로 설정합니다.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]