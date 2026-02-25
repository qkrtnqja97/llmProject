export type Role = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
  timestamp: Date;
}

export interface ChatResponse {
  answer: string;
  source_nodes?: any[]; // RAG 결과 포함 대비
}
