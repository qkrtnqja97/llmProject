/**
 * STT (Speech-to-Text) 서비스
 * 브라우저의 Web Speech Recognition API를 사용하여 음성을 텍스트로 변환
 */

const STT_LANG_MAP: Record<string, string> = {
  ko: "ko-KR",
  en: "en-US",
  ja: "ja-JP",
  "zh-CN": "zh-CN",
  "zh-TW": "zh-TW",
  es: "es-ES",
  fr: "fr-FR",
  de: "de-DE",
  ru: "ru-RU",
};

export interface STTOptions {
  language?: string;
  continuous?: boolean;
  interimResults?: boolean;
  maxAlternatives?: number;
  onResult?: (transcript: string, isFinal: boolean) => void;
  onError?: (error: string) => void;
  onStart?: () => void;
  onEnd?: () => void;
}

export interface STTErrorMap {
  [key: string]: string;
}

const ERROR_MESSAGES: STTErrorMap = {
  "no-speech":
    "음성이 감지되지 않았습니다. 마이크에 가까이서 다시 말해 주세요.",
  "audio-capture": "마이크를 찾을 수 없습니다. 마이크 연결을 확인해 주세요.",
  "not-allowed":
    "마이크 접근이 거부되었습니다. 브라우저 설정에서 마이크를 허용해 주세요.",
  network: "네트워크 오류입니다. 인터넷 연결을 확인해 주세요.",
  aborted: "음성 인식이 중단되었습니다.",
  "language-not-supported": "선택한 언어는 음성 인식을 지원하지 않습니다.",
  "service-not-allowed":
    "이 페이지에서는 음성 인식을 사용할 수 없습니다. (HTTPS 필요)",
  "bad-grammar": "인식에 실패했습니다. 다시 말해 주세요.",
};

let recognitionInstance: any = null;

/**
 * STT 지원 확인
 */
export const isSTTSupported = (): boolean => {
  const SpeechRecognition =
    (window as any).SpeechRecognition ||
    (window as any).webkitSpeechRecognition;
  return !!SpeechRecognition;
};

/**
 * 음성 인식 시작
 */
export const startRecognition = (
  langCode: string = "ko",
  options: STTOptions = {},
): void => {
  if (!isSTTSupported()) {
    alert(
      "이 브라우저는 음성 인식을 지원하지 않습니다. Chrome을 사용해 주세요.",
    );
    return;
  }

  const SpeechRecognition =
    (window as any).SpeechRecognition ||
    (window as any).webkitSpeechRecognition;

  recognitionInstance = new SpeechRecognition();
  recognitionInstance.lang = STT_LANG_MAP[langCode] || langCode || "ko-KR";
  recognitionInstance.continuous = options.continuous ?? false;
  recognitionInstance.interimResults = options.interimResults ?? false;
  recognitionInstance.maxAlternatives = options.maxAlternatives ?? 1;

  if (options.onStart) {
    recognitionInstance.onstart = options.onStart;
  }

  recognitionInstance.onresult = (event: any) => {
    let interimTranscript = "";
    let finalTranscript = "";

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;

      if (event.results[i].isFinal) {
        finalTranscript += transcript + " ";
      } else {
        interimTranscript += transcript;
      }
    }

    if (finalTranscript && options.onResult) {
      options.onResult(finalTranscript.trim(), true);
    } else if (interimTranscript && options.onResult) {
      options.onResult(interimTranscript, false);
    }
  };

  recognitionInstance.onerror = (event: any) => {
    const errorMessage =
      ERROR_MESSAGES[event.error] ||
      `오류가 발생했습니다. 다시 시도해 주세요. (${event.error})`;

    if (options.onError) {
      options.onError(errorMessage);
    }
  };

  recognitionInstance.onend = () => {
    if (options.onEnd) {
      options.onEnd();
    }
  };

  recognitionInstance.start();
};

/**
 * 음성 인식 중지
 */
export const stopRecognition = (): void => {
  if (recognitionInstance) {
    recognitionInstance.stop();
  }
};

/**
 * 음성 인식 중단
 */
export const abortRecognition = (): void => {
  if (recognitionInstance) {
    recognitionInstance.abort();
  }
};

/**
 * 언어 코드의 STT 언어를 가져옴
 */
export const getSTTLanguageForCode = (langCode: string): string => {
  return STT_LANG_MAP[langCode] || langCode || "ko-KR";
};

/**
 * STT 에러 메시지 가져오기
 */
export const getSTTErrorMessage = (errorCode: string): string => {
  return ERROR_MESSAGES[errorCode] || "오류가 발생했습니다.";
};
