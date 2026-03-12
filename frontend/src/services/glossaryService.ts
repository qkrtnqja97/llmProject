export interface GlossaryItem {
  id: string;
  source: string;
  target: string;
}

const GLOSSARY_STORAGE_KEY = "glossary";

/**
 * 용어집 항목 추가
 */
export const addGlossaryItem = (
  source: string,
  target: string,
): GlossaryItem => {
  const glossary = getGlossaryList();
  const newItem: GlossaryItem = {
    id: `${Date.now()}-${Math.random()}`,
    source: source.trim(),
    target: target.trim(),
  };

  glossary.push(newItem);
  localStorage.setItem(GLOSSARY_STORAGE_KEY, JSON.stringify(glossary));
  return newItem;
};

/**
 * 모든 용어집 항목 조회 (배열)
 */
export const getGlossaryList = (): GlossaryItem[] => {
  try {
    const stored = localStorage.getItem(GLOSSARY_STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
};

/**
 * 용어집을 객체 형태로 조회 (번역 API용)
 */
export const getGlossaryMap = (): Record<string, string> => {
  const items = getGlossaryList();
  const map: Record<string, string> = {};

  items.forEach((item) => {
    if (item.source.trim() && item.target.trim()) {
      map[item.source.trim()] = item.target.trim();
    }
  });

  return map;
};

/**
 * 용어집 항목 삭제
 */
export const removeGlossaryItem = (id: string): void => {
  const glossary = getGlossaryList();
  const filtered = glossary.filter((item) => item.id !== id);
  localStorage.setItem(GLOSSARY_STORAGE_KEY, JSON.stringify(filtered));
};

/**
 * 용어집 항목 수정
 */
export const updateGlossaryItem = (
  id: string,
  source: string,
  target: string,
): GlossaryItem | null => {
  const glossary = getGlossaryList();
  const item = glossary.find((item) => item.id === id);

  if (!item) return null;

  item.source = source.trim();
  item.target = target.trim();
  localStorage.setItem(GLOSSARY_STORAGE_KEY, JSON.stringify(glossary));

  return item;
};

/**
 * 용어집 전체 삭제
 */
export const clearGlossary = (): void => {
  localStorage.removeItem(GLOSSARY_STORAGE_KEY);
};

/**
 * 용어 검색
 */
export const searchGlossary = (query: string): GlossaryItem[] => {
  const glossary = getGlossaryList();
  const lowerQuery = query.toLowerCase();

  return glossary.filter(
    (item) =>
      item.source.toLowerCase().includes(lowerQuery) ||
      item.target.toLowerCase().includes(lowerQuery),
  );
};

/**
 * 용어집 항목이 있는지 확인
 */
export const hasGlossaryItems = (): boolean => {
  return getGlossaryList().length > 0;
};
