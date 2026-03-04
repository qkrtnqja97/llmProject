/**
 * TTS (Text-to-Speech) 서비스
 * 브라우저의 Web Speech API를 사용하여 텍스트를 음성으로 읽음
 */

const TTS_LANG_MAP: Record<string, string> = {
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

/**
 * 텍스트를 음성으로 읽음
 * @param text - 읽을 텍스트
 * @param langCode - 언어 코드 (ko, en, ja 등)
 * @param rate - 음성 속도 (기본값 0.9)
 * @param onEnd - 읽기 완료 콜백
 */
export const speakText = (
  text: string,
  langCode: string = "ko",
  rate: number = 0.9,
  onEnd?: () => void,
): void => {
  if (!text?.trim()) {
    console.warn("ttsService: 빈 텍스트는 재생할 수 없습니다.");
    return;
  }

  if (!("speechSynthesis" in window)) {
    alert("이 브라우저는 음성 읽기를 지원하지 않습니다.");
    return;
  }

  // 기존 음성 재생 중단
  speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text.trim());
  utterance.lang = TTS_LANG_MAP[langCode] || langCode || "en-US";
  utterance.rate = rate;

  if (onEnd) {
    utterance.onend = onEnd;
  }

  speechSynthesis.speak(utterance);
};

/**
 * 현재 재생 중인 음성 중단
 */
export const cancelSpeech = (): void => {
  if ("speechSynthesis" in window) {
    speechSynthesis.cancel();
  }
};

/**
 * TTS 지원 확인
 */
export const isTTSSupported = (): boolean => {
  return "speechSynthesis" in window;
};

/**
 * 언어 코드의 TTS 렌글을 가져옴
 */
export const getTTSLanguageForCode = (langCode: string): string => {
  return TTS_LANG_MAP[langCode] || langCode || "en-US";
};
