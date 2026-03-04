export interface TranslationHistory {
  orig: string;
  trans: string;
  source: string;
  target: string;
  ts: number;
}

const HISTORY_STORAGE_KEY = "transHistory";
const MAX_HISTORY_ITEMS = 50;

/**
 * 히스토리에 항목 추가
 */
export const addToHistory = (
  originalText: string,
  translatedText: string,
  source: string,
  target: string,
): void => {
  const history = getHistory();
  const newEntry: TranslationHistory = {
    orig: originalText,
    trans: translatedText,
    source,
    target,
    ts: Date.now(),
  };

  history.unshift(newEntry);
  const trimmedHistory = history.slice(0, MAX_HISTORY_ITEMS);
  localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(trimmedHistory));
};

/**
 * 모든 히스토리 조회
 */
export const getHistory = (): TranslationHistory[] => {
  try {
    const stored = localStorage.getItem(HISTORY_STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
};

/**
 * 특정 인덱스의 히스토리 항목 조회
 */
export const getHistoryItem = (index: number): TranslationHistory | null => {
  const history = getHistory();
  return history[index] || null;
};

/**
 * 히스토리 전체 삭제
 */
export const clearHistory = (): void => {
  localStorage.removeItem(HISTORY_STORAGE_KEY);
};

/**
 * 특정 항목 삭제
 */
export const removeHistoryItem = (index: number): void => {
  const history = getHistory();
  history.splice(index, 1);
  localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(history));
};

/**
 * 히스토리 검색
 */
export const searchHistory = (query: string): TranslationHistory[] => {
  const history = getHistory();
  const lowerQuery = query.toLowerCase();
  return history.filter(
    (item) =>
      item.orig.toLowerCase().includes(lowerQuery) ||
      item.trans.toLowerCase().includes(lowerQuery),
  );
};
