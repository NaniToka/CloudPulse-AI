/**
 * Frontend Service Client for RAG AI Infrastructure Chat Platform
 */

import apiClient from "@/lib/api";
import type {
  RAGQueryResponse,
  RAGUploadResponse,
  RAGHistoryResponse,
} from "@/types/ragChat";

export interface RAGQueryPayload {
  question: string;
  collection_filter?: string[];
  conversation_id?: string;
}

export const ragChatService = {
  async query(payload: RAGQueryPayload): Promise<RAGQueryResponse> {
    const response = await apiClient.post<RAGQueryResponse>("/chat/query", payload);
    return response.data;
  },

  async uploadDocument(file: File, collection: string = "logs"): Promise<RAGUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiClient.post<RAGUploadResponse>("/chat/upload", formData, {
      params: { collection },
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  async getHistory(conversationId: string): Promise<RAGHistoryResponse> {
    const response = await apiClient.get<RAGHistoryResponse>("/chat/history", {
      params: { conversation_id: conversationId },
    });
    return response.data;
  },

  async clearHistory(conversationId: string): Promise<void> {
    await apiClient.delete("/chat/history", {
      params: { conversation_id: conversationId },
    });
  },

};
