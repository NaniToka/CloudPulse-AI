/**
 * AI Copilot service.
 *
 * Non-streaming path  → standard Axios POST, returns ChatResponse.
 * Streaming path      → native fetch() with ReadableStream so we can
 *                       process SSE chunks incrementally without a
 *                       third-party EventSource library.
 *
 * SSE protocol (matches backend _sse_generator):
 *   data: <text chunk>\n\n     — partial content (newlines encoded as \n)
 *   data: [DONE]\n\n            — stream finished
 *   data: [ERROR] <msg>\n\n    — stream error
 */

import apiClient from "@/lib/api";
import type { ChatRequest, ChatResponse, HistoryResponse } from "@/types/ai";

const BASE_URL: string = (
  import.meta.env.VITE_API_BASE_URL ?? "/api/v1"
).replace(/\/+$/, "");


// ─── Non-streaming chat ───────────────────────────────────────────────────────

export const aiService = {
  async chat(data: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>("/ai/chat", {
      ...data,
      stream: false,
    });
    return response.data;
  },

  async getHistory(): Promise<HistoryResponse> {
    const response = await apiClient.get<HistoryResponse>("/ai/history");
    return response.data;
  },

  async clearHistory(): Promise<void> {
    await apiClient.delete("/ai/history");
  },
};

// ─── Streaming chat ───────────────────────────────────────────────────────────

/**
 * Send a message and stream the reply via SSE.
 *
 * @param message      User's message text
 * @param sessionId    Optional existing session UUID
 * @param onChunk      Called with each decoded text chunk as it arrives
 * @param onDone       Called with the full assembled reply when streaming ends
 * @param onError      Called with an error message string on failure
 */
export async function streamChat(
  message: string,
  sessionId: string | undefined,
  onChunk: (chunk: string) => void,
  onDone: (sessionId: string) => void,
  onError: (error: string) => void
): Promise<void> {
  const token = localStorage.getItem("access_token");

  const body: ChatRequest = {
    message,
    session_id: sessionId,
    stream: true,
  };

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}/ai/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(body),
    });
  } catch {
    onError("Network error — could not reach the AI service.");
    return;
  }

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    try {
      const json = JSON.parse(text);
      onError(json.error ?? json.detail ?? `Server error ${response.status}`);
    } catch {
      onError(`Server error ${response.status}`);
    }
    return;
  }

  // The backend streams SSE but does NOT send a session_id in the stream.
  // We need to parse it from a separate response header or from the first
  // non-streaming response.  Since the session is created server-side before
  // streaming starts we can get it from the X-Session-Id response header.
  // (Backend sets it — see ai.py patch below; fall back to undefined.)
  const streamedSessionId = response.headers.get("X-Session-Id") ?? undefined;

  const reader = response.body?.getReader();
  if (!reader) {
    onError("Stream not available.");
    return;
  }

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    let streamDone = false;
    while (!streamDone) {
      const { done, value } = await reader.read();
      if (done) {
        streamDone = true;
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() ?? "";           // keep incomplete last frame

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const payload = line.slice(6);       // strip "data: " prefix

        if (payload === "[DONE]") {
          onDone(streamedSessionId ?? "");
          return;
        }
        if (payload.startsWith("[ERROR]")) {
          onError(payload.slice(8).trim());
          return;
        }
        // Unescape \n that the backend encoded to keep SSE framing intact
        onChunk(payload.replace(/\\n/g, "\n"));
      }
    }
  } finally {
    reader.releaseLock();
  }

  onDone(streamedSessionId ?? "");
}
