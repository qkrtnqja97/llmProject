// frontend/src/services/api.ts

const BASE_URL = "http://localhost:8000";

// 공통 요청 함수
async function request(path: string, options?: RequestInit) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  // 응답은 일단 any로 처리 (타입 나중에 분리 가능)
  return res.json();
}

// LLM + RAG 챗봇 호출
export async function askLLM(
  question: string,
  mode: "auto" | "doc_qa" | "free_chat" = "auto"
) {
  return request("/api/chat", {
    method: "POST",
    body: JSON.stringify({ question, mode }),
  });
}

// 문서 검색 (RAG 검색)
export async function searchWorkspace(query: string) {
  return request("/api/search", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}