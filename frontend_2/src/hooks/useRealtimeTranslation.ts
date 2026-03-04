import { useState, useCallback, useRef, useEffect } from "react";
import {
  translateText,
  TranslationResponse,
} from "@services/translationService";

export const useRealtimeTranslation = (debounceDelay: number = 800) => {
  const [text, setText] = useState("");
  const [result, setResult] = useState<TranslationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const performTranslation = useCallback(
    async (
      inputText: string,
      source: string,
      target: string,
      useLlm: boolean,
    ) => {
      // 이전 요청 취소
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      if (!inputText.trim()) {
        setResult(null);
        setIsLoading(false);
        return;
      }

      const controller = new AbortController();
      abortControllerRef.current = controller;

      setIsLoading(true);
      setError(null);

      try {
        const response = await translateText({
          text: inputText,
          source,
          target,
          use_llm: useLlm,
          glossary: null,
          // signal: controller.signal // 서비스에서 지원한다면 추가
        });

        // Abort된 요청이 아닐 때만 결과 세팅
        if (!controller.signal.aborted) {
          setResult(response);
        }
      } catch (err: any) {
        if (err.name === "AbortError") return; // 취소된 요청은 에러 처리 안 함
        setError(err?.response?.data?.detail || err?.message || "번역 실패");
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    },
    [],
  );

  const handleTextChange = useCallback(
    (inputText: string, source: string, target: string, useLlm: boolean) => {
      setText(inputText);

      if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);

      // 빈 값인 경우 즉시 초기화 (UX 향상)
      if (!inputText.trim()) {
        setResult(null);
        setIsLoading(false);
        return;
      }

      debounceTimerRef.current = setTimeout(() => {
        performTranslation(inputText, source, target, useLlm);
      }, debounceDelay);
    },
    [performTranslation, debounceDelay],
  );

  const clear = useCallback(() => {
    if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
    if (abortControllerRef.current) abortControllerRef.current.abort();
    setText("");
    setResult(null);
    setError(null);
    setIsLoading(false);
  }, []);

  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
      if (abortControllerRef.current) abortControllerRef.current.abort();
    };
  }, []);

  return { text, result, isLoading, error, handleTextChange, setText, clear };
};
