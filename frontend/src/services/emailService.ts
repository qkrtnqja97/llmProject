/**
 * 이메일 파싱 서비스
 */

export interface ParsedEmail {
  from: string | null;
  subject: string | null;
  body: string;
}

/**
 * 이메일 텍스트를 파싱하여 발신자, 제목, 본문으로 분리
 * @param raw - 원본 이메일 텍스트
 * @returns 파싱된 이메일 객체
 */
export const parseEmail = (raw: string): ParsedEmail => {
  const lines = raw.split(/\r?\n/);
  let from = "";
  let subject = "";
  let bodyStart = -1;

  // 최대 30줄까지 헤더 파싱
  for (let i = 0; i < Math.min(lines.length, 30); i++) {
    const line = lines[i];

    // From: 패턴 찾기
    if (/^From:\s*/i.test(line)) {
      from = line.replace(/^From:\s*/i, "").trim();
    }
    // Subject: 패턴 찾기
    else if (/^Subject:\s*/i.test(line)) {
      subject = line.replace(/^Subject:\s*/i, "").trim();
    }
    // 빈 줄 찾기 (헤더 끝)
    else if (line.trim() === "" && i > 0) {
      bodyStart = i + 1;
      break;
    }
  }

  // 본문 시작점을 찾지 못한 경우
  if (bodyStart < 0) {
    bodyStart = 0;
  }

  const body = lines.slice(bodyStart).join("\n").trim() || raw;

  return {
    from: from || null,
    subject: subject || null,
    body: body,
  };
};

/**
 * 이메일 형식으로 텍스트 생성
 */
export const formatEmailText = (
  from: string | null | undefined,
  subject: string | null | undefined,
  body: string,
): string => {
  const parts: string[] = [];

  if (from) {
    parts.push(`From: ${from}`);
  }
  if (subject) {
    parts.push(`Subject: ${subject}`);
  }
  if (from || subject) {
    parts.push(""); // 헤더와 본문 사이에 빈 줄
  }
  parts.push(body);

  return parts.join("\n");
};

/**
 * HTML 이스케이프 처리
 */
export const escapeHtml = (text: string): string => {
  if (!text) return "";

  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
};

/**
 * 이메일 형식 검증
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};
