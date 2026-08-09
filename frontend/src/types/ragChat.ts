/**
 * TypeScript Type Definitions for RAG AI Infrastructure Chat Platform
 */

export interface SourceCitation {
  collection: "logs" | "incidents" | "metrics" | "alerts" | "traces" | "ai_reports";
  title: string;
  snippet: string;
  relevance_score: number;
  metadata: Record<string, any>;
}

export interface RelatedItem {
  type: "alert" | "trace" | "incident";
  id: string;
  title: string;
  status: string;
  severity?: string;
}

export interface RAGQueryResponse {
  id: string;
  conversation_id: string;
  question: string;
  answer: string;
  provider?: string;
  evidence_sources: SourceCitation[];
  confidence_score: number;
  related_alerts: RelatedItem[];
  related_traces: RelatedItem[];
  related_incidents: RelatedItem[];
  recommended_actions: string[];
  suggested_followup_questions: string[];
  created_at: string;
}


export interface RAGUploadResponse {
  filename: string;
  file_size_bytes: number;
  collection: string;
  documents_indexed: number;
  status: string;
  message: string;
}

export interface RAGHistoryItem {
  id: string;
  question: string;
  answer: string;
  confidence_score: number;
  created_at: string;
}

export interface RAGHistoryResponse {
  conversation_id: string;
  messages: RAGHistoryItem[];
  total_messages: number;
}
