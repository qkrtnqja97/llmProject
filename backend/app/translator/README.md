# 하이브리드 번역기

**무료 번역(deep-translator) + Ollama 로컬 LLM 보정**으로 문맥에 맞는 자연스러운 번역을 제공합니다.

## 실행 전 준비

### 1. Ollama 설치 및 모델 다운로드

1. [Ollama 공식 사이트](https://ollama.com)에서 다운로드 후 설치
2. 터미널(또는 PowerShell)에서 모델 다운로드:

```powershell
ollama pull llama3.2
```

다른 모델도 사용 가능: `ollama pull mistral`, `ollama pull phi3` 등

### 2. Python 패키지 설치 (Python 3.10+ 권장)

**Conda 사용 시:**

```powershell
cd "c:\Users\Roy_Koh\Desktop\간단 프로젝트"
conda create -n translator python=3.10 -y
conda activate translator
pip install -r requirements.txt
```

**venv 사용 시:**

```powershell
cd "c:\Users\Roy_Koh\Desktop\간단 프로젝트"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. 실행

```powershell
conda activate translator   # Conda 사용 시 (또는 venv: .\venv\Scripts\Activate.ps1)
python app.py
```

또는 `uvicorn app:app --reload --port 5000`

브라우저에서 http://localhost:5000 접속

**API 문서(Swagger):** http://localhost:5000/docs  
**ReDoc:** http://localhost:5000/redoc

## 사용법

### 바이어 메일 번역
- **바이어 메일** 탭에서 해외 바이어가 보낸 이메일 전체를 붙여넣기
- From, Subject, 본문을 자동 파싱 후 제목·본문 번역 (기본: 영어 → 한국어)
- **전체 복사** 버튼으로 번역된 메일 복사

### 실시간 통역
- **⌨️ 타이핑**: 입력 후 0.8초 대기 시 자동 번역
- **🎤 음성**: 말하기 → 인식 → 번역 → 음성 출력
- **💬 대화**: 내가 말하기 / 상대가 말하기로 양방향 통역. 대화 내용을 회의록으로 TXT 다운로드 가능

### 기본 번역
- **원문/대상 언어** 드롭다운으로 언어 선택
- 텍스트 입력 후 **번역하기** 클릭
- **복사** 버튼으로 결과 클립보드 복사
- **최종 | 기계 번역 | LLM 보정** 탭으로 결과 비교
- **용어집**: + 용어 추가로 전문 용어 지정 (예: API → API)
- **번역 히스토리**: 최근 50개 저장, 클릭 시 입력란에 복원

### 배치 번역
- 한 줄에 한 문장씩 입력 후 **배치 번역**

### 파일 번역
- txt, docx 파일을 끌어다 놓거나 선택 후 **파일 번역**

### 다국어 동시 번역
- 대상 언어를 복수 선택 후 **다국어 번역**

### 기타
- **라이트/다크 모드** 토글
- `Ctrl + Enter`로 빠르게 번역

## 환경 변수 (선택)

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API 주소 |
| `OLLAMA_MODEL` | `llama3.2` | 사용할 Ollama 모델 이름 |

## 지원 언어

한국어, 영어, 일본어, 중국어(간체/번체), 스페인어, 프랑스어, 독일어, 러시아어
