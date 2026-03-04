import { useState, useCallback } from "react";
import {
  translateText,
  translateBatch,
  translateFile,
  translateEmail,
  translateMulti,
  TranslationResponse,
  BatchTranslationResponse,
  EmailTranslationResponse,
  MultiTranslationResponse,
} from "@services/translationService";
import {
  getHistory,
  addToHistory,
  clearHistory,
  removeHistoryItem,
} from "@services/historyService";
import {
  getGlossaryList,
  getGlossaryMap,
  addGlossaryItem as addGlossaryItemService,
  removeGlossaryItem,
} from "@services/glossaryService";

/**
 * 번역 상태 관리 Hook
 */
export const useTranslation = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TranslationResponse | null>(null);

  const translate = useCallback(
    async (
      text: string,
      source: string,
      target: string,
      useLlm: boolean = false,
    ) => {
      if (!text.trim()) {
        setError("텍스트를 입력하세요.");
        return null;
      }

      setIsLoading(true);
      setError(null);

      try {
        const glossary = getGlossaryMap();
        const response = await translateText({
          text,
          source,
          target,
          use_llm: useLlm,
          glossary: Object.keys(glossary).length > 0 ? glossary : null,
        });

        setResult(response);
        addToHistory(text, response.translation, source, target);
        return response;
      } catch (err: any) {
        const errorMsg =
          err?.response?.data?.detail || err?.message || "번역에 실패했습니다.";
        setError(errorMsg);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const clear = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { translate, result, isLoading, error, clear };
};

/**
 * 배치 번역 Hook
 */
export const useBatchTranslation = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<
    BatchTranslationResponse["results"] | null
  >(null);

  const translate = useCallback(
    async (
      texts: string[],
      source: string,
      target: string,
      useLlm: boolean = false,
    ) => {
      const filteredTexts = texts.filter((t) => t.trim());
      if (!filteredTexts.length) {
        setError("번역할 텍스트가 없습니다.");
        return null;
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await translateBatch({
          texts: filteredTexts,
          source,
          target,
          use_llm: useLlm,
        });

        setResults(response.results);
        return response.results;
      } catch (err: any) {
        const errorMsg =
          err?.response?.data?.detail ||
          err?.message ||
          "배치 번역에 실패했습니다.";
        setError(errorMsg);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const clear = useCallback(() => {
    setResults(null);
    setError(null);
  }, []);

  return { translate, results, isLoading, error, clear };
};

/**
 * 파일 번역 Hook
 */
export const useFileTranslation = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<
    BatchTranslationResponse["results"] | null
  >(null);

  const translate = useCallback(
    async (
      file: File,
      source: string,
      target: string,
      useLlm: boolean = false,
    ) => {
      if (!file) {
        setError("파일을 선택하세요.");
        return null;
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await translateFile(file, source, target, useLlm);
        setResults(response.results);
        return response.results;
      } catch (err: any) {
        const errorMsg =
          err?.response?.data?.detail ||
          err?.message ||
          "파일 번역에 실패했습니다.";
        setError(errorMsg);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const clear = useCallback(() => {
    setResults(null);
    setError(null);
  }, []);

  return { translate, results, isLoading, error, clear };
};

/**
 * 이메일 번역 Hook
 */
export const useEmailTranslation = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<EmailTranslationResponse | null>(null);

  const translate = useCallback(
    async (
      fromAddr: string | null,
      subject: string | null,
      body: string,
      source: string,
      target: string,
      useLlm: boolean = false,
    ) => {
      if (!body.trim()) {
        setError("이메일 본문을 입력하세요.");
        return null;
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await translateEmail({
          from_addr: fromAddr,
          subject,
          body,
          source,
          target,
          use_llm: useLlm,
        });

        setResult(response);
        return response;
      } catch (err: any) {
        const errorMsg =
          err?.response?.data?.detail ||
          err?.message ||
          "이메일 번역에 실패했습니다.";
        setError(errorMsg);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const clear = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { translate, result, isLoading, error, clear };
};

/**
 * 다국어 번역 Hook
 */
export const useMultiTranslation = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<
    MultiTranslationResponse["results"] | null
  >(null);

  const translate = useCallback(
    async (
      text: string,
      source: string,
      targets: string[],
      useLlm: boolean = false,
    ) => {
      if (!text.trim()) {
        setError("텍스트를 입력하세요.");
        return null;
      }

      if (!targets.length) {
        setError("대상 언어를 선택하세요.");
        return null;
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await translateMulti({
          text,
          source,
          targets,
          use_llm: useLlm,
        });

        setResults(response.results);
        return response.results;
      } catch (err: any) {
        const errorMsg =
          err?.response?.data?.detail ||
          err?.message ||
          "다국어 번역에 실패했습니다.";
        setError(errorMsg);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const clear = useCallback(() => {
    setResults(null);
    setError(null);
  }, []);

  return { translate, results, isLoading, error, clear };
};

/**
 * 히스토리 관리 Hook
 */
export const useTranslationHistory = () => {
  const [history, setHistory] = useState(getHistory());

  const refresh = useCallback(() => {
    setHistory(getHistory());
  }, []);

  const remove = useCallback(
    (index: number) => {
      removeHistoryItem(index);
      refresh();
    },
    [refresh],
  );

  const clear = useCallback(() => {
    clearHistory();
    refresh();
  }, [refresh]);

  return { history, refresh, remove, clear };
};

/**
 * 용어집 관리 Hook
 */
export const useGlossary = () => {
  const [items, setItems] = useState(getGlossaryList());

  const refresh = useCallback(() => {
    setItems(getGlossaryList());
  }, []);

  const addItem = useCallback(
    (source: string, target: string) => {
      addGlossaryItemService(source, target);
      refresh();
    },
    [refresh],
  );

  const removeItem = useCallback(
    (id: string) => {
      removeGlossaryItem(id);
      refresh();
    },
    [refresh],
  );

  const getMap = useCallback(() => {
    return getGlossaryMap();
  }, []);

  return { items, addItem, removeItem, getMap, refresh };
};
