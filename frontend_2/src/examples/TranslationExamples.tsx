/**
 * 번역 기능 사용 예제 모음
 * 이 파일은 참고용이며, 실제 프로젝트에서는 필요한 컴포넌트를 구현할 때 참고하세요.
 */

// ==================== 기본 번역 예제 ====================
/*
import { useState } from "react";
import { useTranslation } from "@hooks/useTranslation";

export const BasicTranslationExample = () => {
  const [source, setSource] = useState("en");
  const [target, setTarget] = useState("ko");
  const { translate, result, isLoading, error } = useTranslation();

  const handleTranslate = async (text: string) => {
    await translate(text, source, target, false);
  };

  return (
    <div>
      <textarea
        placeholder="번역할 텍스트 입력"
        onBlur={(e) => handleTranslate(e.target.value)}
      />
      {isLoading && <p>번역 중...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {result && <p>{result.translation}</p>}
    </div>
  );
};
*/

// ==================== 실시간 번역 예제 ====================
/*
import { useRealtimeTranslation } from "@hooks/useRealtimeTranslation";

export const RealtimeTranslationExample = () => {
  const [source, setSource] = useState("en");
  const [target, setTarget] = useState("ko");
  const { text, result, isLoading, handleTextChange } = useRealtimeTranslation(
    1000
  );

  return (
    <div>
      <textarea
        value={text}
        onChange={(e) => handleTextChange(e.target.value, source, target)}
        placeholder="여기에 입력하면 자동 번역됩니다"
      />
      <div className="result">
        {isLoading && <p>번역 중...</p>}
        {result && <p>{result.translation}</p>}
      </div>
    </div>
  );
};
*/

// ==================== 음성 인식 + 번역 예제 ====================
/*
import { useSTT } from "@hooks/useSpeech";
import { useTranslation } from "@hooks/useTranslation";

export const VoiceTranslationExample = () => {
  const [source, setSource] = useState("ko");
  const [target, setTarget] = useState("en");
  const { isListening, transcript, startListening, stopListening } = useSTT();
  const { translate, result } = useTranslation();

  const handleVoiceTranslate = async () => {
    startListening(source);
    
    // 음성 인식 완료 후 번역
    setTimeout(async () => {
      if (transcript) {
        await translate(transcript, source, target, false);
      }
    }, 2000);
  };

  return (
    <div>
      <button onClick={handleVoiceTranslate} disabled={isListening}>
        {isListening ? "듣는 중..." : "말하기"}
      </button>
      <p>인식된 텍스트: {transcript}</p>
      {result && <p>번역: {result.translation}</p>}
    </div>
  );
};
*/

// ==================== TTS (음성 읽기) 예제 ====================
/*
import { useTTS } from "@hooks/useSpeech";

export const TextToSpeechExample = () => {
  const { isSpeaking, speak, cancel } = useTTS();

  return (
    <div>
      <button onClick={() => speak("안녕하세요", "ko")} disabled={isSpeaking}>
        {isSpeaking ? "읽는 중..." : "음성으로 읽기"}
      </button>
      <button onClick={cancel} disabled={!isSpeaking}>
        중단
      </button>
    </div>
  );
};
*/

// ==================== 히스토리 관리 예제 ====================
/*
import { useTranslationHistory } from "@hooks/useTranslation";

export const HistoryExample = () => {
  const { history, remove, clear } = useTranslationHistory();

  return (
    <div>
      <h3>번역 히스토리</h3>
      <button onClick={clear}>전체 삭제</button>
      <ul>
        {history.map((item, idx) => (
          <li key={idx}>
            <span>{item.orig} → {item.trans}</span>
            <button onClick={() => remove(idx)}>삭제</button>
          </li>
        ))}
      </ul>
    </div>
  );
};
*/

// ==================== 용어집 관리 예제 ====================
/*
import { useGlossary } from "@hooks/useTranslation";

export const GlossaryExample = () => {
  const { items, addItem, removeItem } = useGlossary();
  const [source, setSource] = useState("");
  const [target, setTarget] = useState("");

  const handleAdd = () => {
    addItem(source, target);
    setSource("");
    setTarget("");
  };

  return (
    <div>
      <h3>용어집</h3>
      <input
        value={source}
        onChange={(e) => setSource(e.target.value)}
        placeholder="원어"
      />
      <input
        value={target}
        onChange={(e) => setTarget(e.target.value)}
        placeholder="번역"
      />
      <button onClick={handleAdd}>추가</button>

      <ul>
        {items.map((item) => (
          <li key={item.id}>
            <span>
              {item.source} → {item.target}
            </span>
            <button onClick={() => removeItem(item.id)}>삭제</button>
          </li>
        ))}
      </ul>
    </div>
  );
};
*/

// ==================== 대화 모드 예제 ====================
/*
import { useConversationMode } from "@hooks/useSpeech";
import { useTranslation } from "@hooks/useTranslation";

export const ConversationModeExample = () => {
  const [source, setSource] = useState("ko");
  const [target, setTarget] = useState("en");
  const { translate } = useTranslation();
  const {
    conversationHistory,
    addToConversation,
    clearConversation,
    downloadAsText,
    stt,
  } = useConversationMode();

  const handleMeSpeak = async () => {
    stt.startListening(source);
    // 인식 완료 후 처리
    setTimeout(async () => {
      if (stt.transcript) {
        const result = await translate(
          stt.transcript,
          source,
          target,
          false
        );
        if (result) {
          addToConversation("나", stt.transcript, result.translation);
        }
      }
    }, 2000);
  };

  return (
    <div>
      <button onClick={handleMeSpeak} disabled={stt.isListening}>
        {stt.isListening ? "듣는 중..." : "나"}
      </button>
      <button onClick={() => downloadAsText("한국어", "영어")}>
        다운로드
      </button>
      <button onClick={clearConversation}>초기화</button>

      <div>
        {conversationHistory.map((item, idx) => (
          <div key={idx}>
            <p>
              [{item.time}] {item.speaker}
            </p>
            <p>{item.original}</p>
            <p>→ {item.translation}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
*/

// ==================== 배치 번역 예제 ====================
/*
import { useBatchTranslation } from "@hooks/useTranslation";

export const BatchTranslationExample = () => {
  const [source, setSource] = useState("en");
  const [target, setTarget] = useState("ko");
  const { translate, results, isLoading } = useBatchTranslation();

  const handleBatchTranslate = async () => {
    const texts = [
      "Hello",
      "Good morning",
      "How are you?",
    ];
    await translate(texts, source, target, false);
  };

  return (
    <div>
      <button onClick={handleBatchTranslate} disabled={isLoading}>
        {isLoading ? "번역 중..." : "배치 번역"}
      </button>
      <div>
        {results?.map((item, idx) => (
          <div key={idx}>
            <p>{item.original}</p>
            <p>→ {item.translation}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
*/

// ==================== 파일 번역 예제 ====================
/*
import { useFileTranslation } from "@hooks/useTranslation";

export const FileTranslationExample = () => {
  const [source, setSource] = useState("en");
  const [target, setTarget] = useState("ko");
  const { translate, results, isLoading } = useFileTranslation();

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      await translate(file, source, target, false);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleFileSelect} disabled={isLoading} />
      {isLoading && <p>번역 중...</p>}
      <div>
        {results?.map((item, idx) => (
          <div key={idx}>
            <p>{item.original}</p>
            <p>→ {item.translation}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
*/

// ==================== 이메일 번역 예제 ====================
/*
import { useEmailTranslation } from "@hooks/useTranslation";
import { parseEmail } from "@services/emailService";

export const EmailTranslationExample = () => {
  const [source, setSource] = useState("en");
  const [target, setTarget] = useState("ko");
  const [emailText, setEmailText] = useState("");
  const { translate, result, isLoading } = useEmailTranslation();

  const handleTranslateEmail = async () => {
    const parsed = parseEmail(emailText);
    await translate(
      parsed.from,
      parsed.subject,
      parsed.body,
      source,
      target,
      false
    );
  };

  return (
    <div>
      <textarea
        value={emailText}
        onChange={(e) => setEmailText(e.target.value)}
        placeholder="이메일 텍스트 입력"
      />
      <button onClick={handleTranslateEmail} disabled={isLoading}>
        {isLoading ? "번역 중..." : "이메일 번역"}
      </button>
      {result && (
        <div>
          {result.from && <p>발신: {result.from}</p>}
          {result.subject_translated && <p>제목: {result.subject_translated}</p>}
          <p>{result.body_translated}</p>
        </div>
      )}
    </div>
  );
};
*/

// ==================== 다국어 번역 예제 ====================
/*
import { useMultiTranslation } from "@hooks/useTranslation";
import { useState } from "react";

export const MultiTranslationExample = () => {
  const [source, setSource] = useState("en");
  const [selectedTargets, setSelectedTargets] = useState<string[]>([
    "ko",
    "ja",
  ]);
  const { translate, results, isLoading } = useMultiTranslation();

  const handleMultiTranslate = async () => {
    await translate("Hello World", source, selectedTargets, false);
  };

  return (
    <div>
      <input type="text" placeholder="텍스트 입력" />
      <button onClick={handleMultiTranslate} disabled={isLoading}>
        {isLoading ? "번역 중..." : "다국어 번역"}
      </button>
      <div>
        {results &&
          Object.entries(results).map(([lang, data]) => (
            <div key={lang}>
              <strong>{lang}:</strong> {data.translation}
            </div>
          ))}
      </div>
    </div>
  );
};
*/

// ==================== 테마 전환 예제 ====================
/*
import { useTheme } from "@context/ThemeContext";

export const ThemeSwitcherExample = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div>
      <p>현재 테마: {theme}</p>
      <button onClick={toggleTheme}>테마 전환</button>
    </div>
  );
};
*/

export default {};
