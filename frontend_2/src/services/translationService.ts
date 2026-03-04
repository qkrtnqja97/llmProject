import apiClient from "./apiClient";

export interface TranslationRequest {
  text: string;
  source: string;
  target: string;
  use_llm: boolean;
  glossary?: Record<string, string> | null;
}

export interface TranslationResponse {
  translation: string;
  rough?: string;
  refined: boolean;
}

export interface BatchTranslationRequest {
  texts: string[];
  source: string;
  target: string;
  use_llm: boolean;
}

export interface BatchTranslationResponse {
  results: {
    original: string;
    translation: string;
  }[];
}

export interface MultiTranslationRequest {
  text: string;
  source: string;
  targets: string[];
  use_llm: boolean;
}

export interface MultiTranslationResponse {
  results: Record<
    string,
    {
      translation: string;
    }
  >;
}

export interface EmailTranslationRequest {
  from_addr: string | null;
  subject: string | null;
  body: string;
  source: string;
  target: string;
  use_llm: boolean;
}

export interface EmailTranslationResponse {
  from?: string;
  subject_translated?: string;
  body_translated: string;
}

/**
 * 기본 번역 요청
 */
export const translateText = async (
  request: TranslationRequest,
): Promise<TranslationResponse> => {
  const response = await apiClient.post<TranslationResponse>(
    "/translate",
    request,
  );
  return response.data;
};

/**
 * 배치 번역 요청 (여러 줄 번역)
 */
export const translateBatch = async (
  request: BatchTranslationRequest,
): Promise<BatchTranslationResponse> => {
  const response = await apiClient.post<BatchTranslationResponse>(
    "/translate/batch",
    request,
  );
  return response.data;
};

/**
 * 파일 번역 요청
 */
export const translateFile = async (
  file: File,
  source: string,
  target: string,
  use_llm: boolean,
): Promise<BatchTranslationResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("source", source);
  formData.append("target", target);
  formData.append("use_llm", String(use_llm));

  const response = await apiClient.post<BatchTranslationResponse>(
    "/translate/file",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    },
  );
  return response.data;
};

/**
 * 이메일 번역 요청
 */
export const translateEmail = async (
  request: EmailTranslationRequest,
): Promise<EmailTranslationResponse> => {
  const response = await apiClient.post<EmailTranslationResponse>(
    "/translate/email",
    request,
  );
  return response.data;
};

/**
 * 다국어 번역 요청
 */
export const translateMulti = async (
  request: MultiTranslationRequest,
): Promise<MultiTranslationResponse> => {
  const response = await apiClient.post<MultiTranslationResponse>(
    "/translate/multi",
    request,
  );
  return response.data;
};
