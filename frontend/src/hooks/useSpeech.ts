import { useState, useCallback, useRef } from "react";
import {
  startRecognition,
  stopRecognition,
  abortRecognition,
  isSTTSupported,
  getSTTErrorMessage,
} from "@services/sttService";
import { speakText, cancelSpeech, isTTSSupported } from "@services/ttsService";

/**
 * STT (Speech-to-Text) Hook
 */
export const useSTT = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);

  const startListening = useCallback((langCode: string = "ko") => {
    if (!isSTTSupported()) {
      setError(
        "이 브라우저는 음성 인식을 지원하지 않습니다. Chrome을 사용해 주세요.",
      );
      return;
    }

    setTranscript("");
    setError(null);
    setIsListening(true);

    try {
      startRecognition(langCode, {
        language: langCode,
        continuous: false,
        interimResults: true,
        onResult: (text, isFinal) => {
          setTranscript(text);
          if (isFinal) {
            setIsListening(false);
          }
        },
        onError: (errorCode) => {
          setError(getSTTErrorMessage(errorCode));
          setIsListening(false);
        },
        onStart: () => {
          setError(null);
        },
        onEnd: () => {
          setIsListening(false);
        },
      });
    } catch (err: any) {
      setError(err?.message || "음성 인식 중 오류가 발생했습니다.");
      setIsListening(false);
    }
  }, []);

  const stopListening = useCallback(() => {
    stopRecognition();
    setIsListening(false);
  }, []);

  const abortListening = useCallback(() => {
    abortRecognition();
    setIsListening(false);
    setTranscript("");
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isListening,
    transcript,
    error,
    startListening,
    stopListening,
    abortListening,
    clearError,
    isSupported: isSTTSupported(),
  };
};

/**
 * TTS (Text-to-Speech) Hook
 */
export const useTTS = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const speak = useCallback((text: string, langCode: string = "ko") => {
    if (!isTTSSupported()) {
      setError("이 브라우저는 음성 읽기를 지원하지 않습니다.");
      return;
    }

    if (!text?.trim()) {
      return;
    }

    setError(null);
    setIsSpeaking(true);

    try {
      speakText(text, langCode, 0.9, () => {
        setIsSpeaking(false);
      });
    } catch (err: any) {
      setError(err?.message || "음성 출력 중 오류가 발생했습니다.");
      setIsSpeaking(false);
    }
  }, []);

  const cancel = useCallback(() => {
    cancelSpeech();
    setIsSpeaking(false);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isSpeaking,
    error,
    speak,
    cancel,
    clearError,
    isSupported: isTTSSupported(),
  };
};

/**
 * 대화 모드 Hook (STT + 번역 + TTS 통합)
 */
export const useConversationMode = () => {
  const [conversationHistory, setConversationHistory] = useState<
    Array<{
      speaker: string;
      original: string;
      translation: string;
      time: string;
    }>
  >([]);
  const stt = useSTT();
  const tts = useTTS();

  const addToConversation = useCallback(
    (speaker: string, original: string, translation: string) => {
      const time = new Date().toLocaleTimeString("ko-KR", {
        hour: "2-digit",
        minute: "2-digit",
      });
      setConversationHistory((prev) => [
        ...prev,
        { speaker, original, translation, time },
      ]);
    },
    [],
  );

  const clearConversation = useCallback(() => {
    setConversationHistory([]);
  }, []);

  const downloadAsText = useCallback(
    (sourceLang: string, targetLang: string) => {
      if (conversationHistory.length === 0) {
        alert("저장할 대화 내용이 없습니다.");
        return;
      }

      let txt = `=== 회의록 ===\n`;
      txt += `일시: ${new Date().toLocaleString("ko-KR")}\n`;
      txt += `언어: ${sourceLang} ↔ ${targetLang}\n`;
      txt += `\n--- 대화 내용 ---\n\n`;

      conversationHistory.forEach((x) => {
        txt += `[${x.time}] ${x.speaker}\n`;
        txt += `${x.original}\n`;
        txt += `→ ${x.translation}\n\n`;
      });

      const blob = new Blob([txt], { type: "text/plain;charset=utf-8" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `회의록_${new Date().toISOString().slice(0, 10)}.txt`;
      a.click();
      URL.revokeObjectURL(a.href);
    },
    [conversationHistory],
  );

  return {
    conversationHistory,
    addToConversation,
    clearConversation,
    downloadAsText,
    stt,
    tts,
  };
};
