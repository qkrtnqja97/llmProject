# 번역 서비스 및 기능 통합 가이드

이 문서는 `main.js`의 기능들을 React 기반의 `frontend`에 통합한 내용을 설명합니다.

## 📦 추가된 서비스 파일

### 1. **translationService.ts**

모든 번역 API 호출을 관리하는 서비스입니다.

**기능:**

- `translateText()` - 기본 번역
- `translateBatch()` - 배치 번역 (여러 줄)
- `translateFile()` - 파일 번역
- `translateEmail()` - 이메일 번역
- `translateMulti()` - 다국어 번역

**사용 예:**

```typescript
import { translateText } from "@services/translationService";

const result = await translateText({
  text: "Hello",
  source: "en",
  target: "ko",
  use_llm: false,
  glossary: null,
});
```

### 2. **historyService.ts**

번역 히스토리를 localStorage에 저장하고 관리합니다.

**기능:**

- `addToHistory()` - 히스토리에 항목 추가
- `getHistory()` - 모든 히스토리 조회
- `clearHistory()` - 히스토리 전체 삭제
- `removeHistoryItem()` - 특정 항목 삭제
- `searchHistory()` - 히스토리 검색

**저장 위치:** `localStorage.transHistory`

### 3. **glossaryService.ts**

번역 용어집을 localStorage에 저장하고 관리합니다.

**기능:**

- `addGlossaryItem()` - 용어 추가
- `getGlossaryList()` - 용어집 리스트 (배열)
- `getGlossaryMap()` - 용어집 객체 (번역 API용)
- `removeGlossaryItem()` - 용어 삭제
- `updateGlossaryItem()` - 용어 수정
- `clearGlossary()` - 용어집 전체 삭제
- `searchGlossary()` - 용어 검색

**저장 위치:** `localStorage.glossary`

### 4. **ttsService.ts**

텍스트를 음성으로 읽어주는 서비스 (Web Speech API 사용)

**기능:**

- `speakText()` - 텍스트 음성 재생
- `cancelSpeech()` - 음성 재생 중단
- `isTTSSupported()` - 지원 여부 확인
- `getTTSLanguageForCode()` - 언어 코드 변환

**지원 언어:**

- ko (한국어), en (영어), ja (일본어)
- zh-CN (중국어 간체), zh-TW (중국어 번체)
- es (스페인어), fr (프랑스어), de (독일어), ru (러시아어)

### 5. **sttService.ts**

음성을 텍스트로 변환하는 서비스 (Web Speech Recognition API 사용)

**기능:**

- `startRecognition()` - 음성 인식 시작
- `stopRecognition()` - 음성 인식 중지
- `abortRecognition()` - 음성 인식 중단
- `isSTTSupported()` - 지원 여부 확인

**특징:**

- 브라우저: Chrome, Edge 등에서 지원
- 중간 결과(interim results) 지원

### 6. **emailService.ts**

이메일 텍스트를 파싱하고 포맷팅합니다.

**기능:**

- `parseEmail()` - 이메일 텍스트 파싱 (발신자, 제목, 본문)
- `formatEmailText()` - 이메일 형식으로 텍스트 생성
- `escapeHtml()` - HTML 이스케이프 처리
- `isValidEmail()` - 이메일 형식 검증

### 7. **utilService.ts**

일반 유틸리티 함수 모음

**주요 기능:**

- `escapeHtml()` - HTML 이스케이프
- `debounce()` - 디바운싱
- `throttle()` - 스로틀링
- `formatDate()` - 날짜 포맷팅
- `formatFileSize()` - 파일 크기 포맷팅
- `truncateText()` - 텍스트 자르기
- `copyToClipboard()` - 클립보드 복사
- 기타 유틸리티 함수들

## 🎣 추가된 Hook

### 1. **useTranslation()**

기본 번역 상태와 로직을 관리합니다.

```typescript
import { useTranslation } from "@hooks/useTranslation";

const { translate, result, isLoading, error, clear } = useTranslation();

// 번역 실행
await translate("Hello", "en", "ko", false);
```

### 2. **useBatchTranslation()**

여러 줄의 텍스트를 한 번에 번역합니다.

```typescript
const { translate, results, isLoading, error } = useBatchTranslation();
await translate(["Hello", "World"], "en", "ko", false);
```

### 3. **useFileTranslation()**

파일 기반 번역을 관리합니다.

```typescript
const { translate, results, isLoading, error } = useFileTranslation();
await translate(file, "en", "ko", false);
```

### 4. **useEmailTranslation()**

이메일 번역을 관리합니다.

```typescript
const { translate, result, isLoading, error } = useEmailTranslation();
await translate(fromAddr, subject, body, "en", "ko", false);
```

### 5. **useMultiTranslation()**

한 텍스트를 여러 언어로 번역합니다.

```typescript
const { translate, results, isLoading, error } = useMultiTranslation();
await translate("Hello", "en", ["ko", "ja", "zh-CN"], false);
```

### 6. **useTranslationHistory()**

번역 히스토리를 관리합니다.

```typescript
const { history, refresh, remove, clear } = useTranslationHistory();
```

### 7. **useGlossary()**

용어집을 관리합니다.

```typescript
const { items, addItem, removeItem, getMap, refresh } = useGlossary();
```

### 8. **useSTT()**

음성 인식을 관리합니다.

```typescript
const { isListening, transcript, error, startListening, stopListening } =
  useSTT();

startListening("ko");
```

### 9. **useTTS()**

음성 재생을 관리합니다.

```typescript
const { isSpeaking, speak, cancel, error } = useTTS();

speak("안녕하세요", "ko");
```

### 10. **useConversationMode()**

대화 모드 (STT + 번역 + TTS 통합)를 관리합니다.

```typescript
const { conversationHistory, addToConversation, downloadAsText, stt, tts } =
  useConversationMode();
```

## 🌓 테마 관리

### **ThemeContext.tsx**

전역 테마 상태를 관리합니다.

**사용:**

```typescript
import { useTheme } from "@context/ThemeContext";

const { theme, setTheme, toggleTheme } = useTheme();
```

**지원 테마:**

- navy (기본값)
- gray
- sand

## 📋 마이그레이션 체크리스트

### main.js의 기능 → React 변환 현황

- [x] 테마 관리 (라이트/다크 모드)
- [x] 기본 번역
- [x] 배치 번역
- [x] 파일 번역
- [x] 이메일 번역
- [x] 실시간 번역 (debounce 포함)
- [x] 음성 인식 번역
- [x] 대화 모드
- [x] 다국어 번역
- [x] TTS (음성 읽기)
- [x] STT (음성 인식)
- [x] 히스토리 관리
- [x] 용어집 관리
- [x] 이메일 파싱
- [x] 유틸리티 함수들

## 🔧 컴포넌트 구현 예제

### 기본 번역 컴포넌트

```typescript
import { useTranslation } from '@hooks/useTranslation';
import { useGlossary } from '@hooks/useTranslation';

export const TranslationPanel = () => {
  const { translate, result, isLoading, error } = useTranslation();
  const { items: glossaryItems } = useGlossary();

  const handleTranslate = async () => {
    await translate("Hello", "en", "ko", false);
  };

  return (
    <div>
      <input placeholder="번역할 텍스트" />
      <button onClick={handleTranslate} disabled={isLoading}>
        {isLoading ? '번역 중...' : '번역하기'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {result && <p>{result.translation}</p>}
    </div>
  );
};
```

## 📝 주의사항

1. **STT/TTS:** Chrome 및 Edge에서 권장됩니다. 다른 브라우저에서는 지원하지 않을 수 있습니다.
2. **HTTPS:** STT는 HTTPS 환경에서만 작동합니다.
3. **localStorage:** 모든 히스토리와 용어집은 localStorage에 저장되므로, 브라우저 캐시 삭제 시 데이터가 손실됩니다.
4. **API 엔드포인트:** translationService는 `/v1` 경로의 백엔드 API를 사용합니다.

## 🚀 다음 단계

이제 이 서비스들을 사용하여:

1. 번역 페이지 컴포넌트 구현
2. 실시간 번역 UI 구현
3. 대화 모드 UI 구현
4. 히스토리 및 용어집 관리 UI 구현

을 수행할 수 있습니다.
