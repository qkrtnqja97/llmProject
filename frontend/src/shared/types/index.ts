// src/shared/types/index.ts

export type Role = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
  timestamp: Date;
}

export interface CompanyInfo {
  name: string;
  logoUrl?: string;
  address?: string;
}

export interface MenuItem {
  id: string;
  label: string;
  path: string;
  pinned?: boolean;
  visible?: boolean;
}
