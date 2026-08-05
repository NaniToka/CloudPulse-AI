/**
 * RAG AI Infrastructure Chat Platform — Main Page
 */

import React, { useState, useRef, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Sparkles,
  Send,
  Upload,
  Trash2,
  Download,
  Bot,
  RefreshCw,
  Database,
  FileText,
} from "lucide-react";

import PageHeader from "@/components/shared/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/hooks/useToast";

import { ragChatService } from "@/services/ragChatService";
import { RAGSuggestedPrompts } from "@/components/ragChat/RAGSuggestedPrompts";
import { RAGChatMessage } from "@/components/ragChat/RAGChatMessage";
import type { RAGQueryResponse } from "@/types/ragChat";

export default function RAGChatPage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [conversationId] = useState("conv-session-1");
  const [questionInput, setQuestionInput] = useState("");
  const [messages, setMessages] = useState<RAGQueryResponse[]>([]);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // RAG Query Mutation
  const queryMutation = useMutation({
    mutationFn: (q: string) =>
      ragChatService.query({ question: q, conversation_id: conversationId }),
    onSuccess: (res) => {
      setMessages((prev) => [...prev, res]);
    },
    onError: (err: any) => {
      toast({
        title: "Chat query failed",
        description: err?.response?.data?.detail || "Could not query RAG pipeline.",
        variant: "destructive",
      });
    },
  });

  // File Upload Mutation
  const uploadMutation = useMutation({
    mutationFn: (file: File) => ragChatService.uploadDocument(file, "logs"),
    onSuccess: (res) => {
      toast({
        title: "Telemetry File Indexed",
        description: `${res.filename} indexed into '${res.collection}' vector store.`,
      });
    },
  });

  // Clear History Mutation
  const clearMutation = useMutation({
    mutationFn: () => ragChatService.clearHistory(conversationId),
    onSuccess: () => {
      setMessages([]);
      toast({
        title: "History Cleared",
        description: "RAG chat session history wiped.",
      });
    },
  });

  const handleSend = (q?: string) => {
    const targetQ = q || questionInput;
    if (!targetQ.trim() || queryMutation.isPending) return;

    setQuestionInput("");
    queryMutation.mutate(targetQ);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      uploadMutation.mutate(e.target.files[0]);
    }
  };

  const handleExportConversation = () => {
    const text = messages
      .map((m) => `User: ${m.question}\nAI: ${m.answer}\nConfidence: ${m.confidence_score}\n---`)
      .join("\n\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `rag_chat_transcript_${Date.now()}.txt`;
    a.click();
  };

  return (
    <div className="space-y-6 flex flex-col h-[calc(100vh-100px)] max-h-[900px]">
      {/* Page Header */}
      <PageHeader
        title="AI Infrastructure Chat (RAG)"
        subtitle="Retrieval-Augmented Generation assistant answering queries across ChromaDB telemetry vector collections"
        actions={
          <div className="flex items-center gap-2">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              className="hidden"
              accept=".log,.json,.txt,.csv"
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadMutation.isPending}
              className="gap-2 text-xs"
            >
              <Upload className="h-3.5 w-3.5" /> Upload Telemetry File
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={handleExportConversation}
              disabled={messages.length === 0}
              className="gap-2 text-xs"
            >
              <Download className="h-3.5 w-3.5" /> Export
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => clearMutation.mutate()}
              disabled={messages.length === 0}
              className="gap-2 text-xs text-red-400 hover:text-red-300"
            >
              <Trash2 className="h-3.5 w-3.5" /> Clear History
            </Button>
          </div>
        }
      />

      {/* Main Conversation Chat Box */}
      <Card className="border border-white/10 bg-bg-surface/80 backdrop-blur-md shadow-2xl flex-1 flex flex-col justify-between overflow-hidden">
        <CardContent className="p-6 flex-1 overflow-y-auto space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 space-y-4 my-auto">
              <div className="h-16 w-16 rounded-2xl bg-brand-purple/10 border border-brand-purple/20 flex items-center justify-center text-brand-purple shadow-glow-blue">
                <Bot className="h-8 w-8" />
              </div>
              <div>
                <h3 className="text-base font-bold text-foreground">
                  Ask CloudPulse RAG AI Anything About Your Infrastructure
                </h3>
                <p className="text-xs text-muted-foreground max-w-md mt-1">
                  Query real-time metrics, log files, incidents, distributed traces, and FinOps cost reports.
                </p>
              </div>
              <div className="w-full max-w-xl pt-4">
                <RAGSuggestedPrompts onSelectPrompt={(p) => handleSend(p)} />
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg, idx) => (
                <RAGChatMessage key={idx} message={msg} onSelectFollowup={(fq) => handleSend(fq)} />
              ))}

              {queryMutation.isPending && (
                <div className="flex justify-start">
                  <div className="bg-bg-elevated/80 border border-white/10 p-4 rounded-2xl text-xs text-muted-foreground font-mono flex items-center gap-2 animate-pulse">
                    <Sparkles className="h-4 w-4 text-brand-purple animate-spin" />
                    Synthesizing RAG context across ChromaDB collections...
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </CardContent>

        {/* Input Bar Footer */}
        <div className="p-4 border-t border-white/10 bg-bg-elevated/40 space-y-3">
          {messages.length > 0 && (
            <RAGSuggestedPrompts onSelectPrompt={(p) => handleSend(p)} disabled={queryMutation.isPending} />
          )}

          <div className="flex items-center gap-2">
            <Input
              type="text"
              placeholder="Ask about CPU metrics, slow traces, cost optimizations, or incidents..."
              value={questionInput}
              onChange={(e) => setQuestionInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              disabled={queryMutation.isPending}
              className="flex-1 bg-bg-surface border-white/10 text-xs focus:border-brand-purple h-10"
            />

            <Button
              disabled={!questionInput.trim() || queryMutation.isPending}
              onClick={() => handleSend()}
              className="bg-brand-purple hover:bg-brand-purple/90 text-white h-10 px-4 gap-2 text-xs"
            >
              <Send className="h-4 w-4" /> Send
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
