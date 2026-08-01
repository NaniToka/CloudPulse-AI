// ─── API request / response shapes (mirror backend schemas) ─────────────────

export interface ChatRequest {
  message: string;
  session_id?: string;
  stream: boolean;
}

export interface ChatResponse {
  session_id: string;
  message_id: string;
  reply: string;
  model: string;
}

export interface MessageSchema {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface SessionSchema {
  id: string;
  title: string | null;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
  messages: MessageSchema[];
}

export interface HistoryResponse {
  sessions: SessionSchema[];
  total: number;
}

// ─── Local UI state ───────────────────────────────────────────────────────────

export interface LocalMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  /** True while a streaming response is still arriving */
  streaming?: boolean;
  /** Non-null when the message failed to send */
  error?: string;
}
