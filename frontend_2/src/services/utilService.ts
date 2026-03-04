/**
 * 일반 유틸리티 함수 모음
 */

/**
 * HTML 문자열 이스케이프 처리
 * XSS 공격 방지를 위해 사용
 */
export const escapeHtml = (text: string | undefined | null): string => {
  if (!text) return "";

  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
};

/**
 * 디바운스 함수
 * @param func - 실행할 함수
 * @param delay - 지연 시간 (ms)
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

/**
 * 스로틀 함수
 * @param func - 실행할 함수
 * @param limit - 제한 시간 (ms)
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * 날짜 포맷팅
 * @param date - Date 객체 또는 타임스탬프
 * @param format - 포맷 문자열 (기본값: 'YYYY-MM-DD HH:mm:ss')
 */
export const formatDate = (
  date: Date | number,
  format: string = "YYYY-MM-DD HH:mm:ss"
): string => {
  const d = typeof date === "number" ? new Date(date) : date;

  const pad = (num: number): string => String(num).padStart(2, "0");

  const replacements: Record<string, string> = {
    YYYY: String(d.getFullYear()),
    MM: pad(d.getMonth() + 1),
    DD: pad(d.getDate()),
    HH: pad(d.getHours()),
    mm: pad(d.getMinutes()),
    ss: pad(d.getSeconds()),
  };

  return format.replace(/YYYY|MM|DD|HH|mm|ss/g, (match) => replacements[match]);
};

/**
 * 상대 시간 표시 (예: '2분 전', '1시간 전')
 */
export const formatRelativeTime = (date: Date | number): string => {
  const now = new Date();
  const d = typeof date === "number" ? new Date(date) : date;
  const diffMs = now.getTime() - d.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSeconds < 60) return "방금 전";
  if (diffMinutes < 60) return `${diffMinutes}분 전`;
  if (diffHours < 24) return `${diffHours}시간 전`;
  if (diffDays < 7) return `${diffDays}일 전`;

  return formatDate(d, "YYYY-MM-DD");
};

/**
 * 파일 크기 포맷팅
 * @param bytes - 파일 크기 (바이트)
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return "0 B";

  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
};

/**
 * 숫자 포맷팅 (천 단위 구분)
 * @param num - 숫자
 */
export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat("ko-KR").format(num);
};

/**
 * 문자열 잘라내기
 * @param text - 원본 텍스트
 * @param maxLength - 최대 길이
 * @param suffix - 생략 텍스트 (기본값: '...')
 */
export const truncateText = (
  text: string,
  maxLength: number,
  suffix: string = "..."
): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + suffix;
};

/**
 * UUID 생성
 */
export const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * 클립보드에 텍스트 복사
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error("클립보드 복사 실패:", err);
    return false;
  }
};

/**
 * 딕셔너리가 비었는지 확인
 */
export const isEmptyObject = (obj: Record<string, any>): boolean => {
  return Object.keys(obj).length === 0;
};

/**
 * 배열을 청크로 분할
 */
export const chunkArray = <T>(array: T[], size: number): T[][] => {
  const chunks: T[][] = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
};

/**
 * 객체 병합
 */
export const mergeObjects = <T extends Record<string, any>>(
  ...objects: T[]
): T => {
  return objects.reduce((acc, obj) => ({ ...acc, ...obj }), {} as T);
};

/**
 * 조건부 클래스 이름 생성 (className 관리)
 */
export const classNames = (
  ...classes: (string | undefined | null | boolean)[]
): string => {
  return classes.filter((c) => typeof c === "string").join(" ");
};
