import React, { useState, useEffect, useRef, useCallback } from "react";
import { RefreshCw, Sparkles, FileText, Upload, History as HistoryIcon } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import { Button } from "@/components/ui/button";
import LogUploader from "@/components/logs/LogUploader";
import AiAnalysisPanel from "@/components/logs/AiAnalysisPanel";
import LogViewer from "@/components/logs/LogViewer";
import AnalysisHistory from "@/components/logs/AnalysisHistory";
import { logService } from "@/services/logService";
import type { LogAnalysis, AnalysisListItem } from "@/types/log_analysis";

export default function LogsPage() {
  const [history, setHistory] = useState<AnalysisListItem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [currentAnalysis, setCurrentAnalysis] = useState<LogAnalysis | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);
  const [isAnalysisLoading, setIsAnalysisLoading] = useState(false);

  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Load analysis history on mount
  const loadHistory = useCallback(async () => {
    try {
      setIsHistoryLoading(true);
      const res = await logService.getHistory();
      setHistory(res.items);
      if (res.items.length > 0 && !selectedId) {
        setSelectedId(res.items[0].id);
      }
    } catch (err) {
      console.error("Failed to load log history", err);
    } finally {
      setIsHistoryLoading(false);
    }
  }, [selectedId]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const stopPolling = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  }, []);

  const startPolling = useCallback((id: string) => {
    stopPolling();
    pollIntervalRef.current = setInterval(async () => {
      try {
        const updated = await logService.getAnalysis(id);
        setCurrentAnalysis(updated);
        if (updated.status === "complete" || updated.status === "error") {
          stopPolling();
          loadHistory();
        }
      } catch (err) {
        console.error("Error polling log analysis status", err);
        stopPolling();
      }
    }, 2500);
  }, [loadHistory, stopPolling]);

  // Fetch selected analysis details
  const fetchAnalysisDetail = useCallback(async (id: string) => {
    try {
      setIsAnalysisLoading(true);
      const detail = await logService.getAnalysis(id);
      setCurrentAnalysis(detail);

      // If status is "analyzing" or "pending", start polling
      if (detail.status === "analyzing" || detail.status === "pending") {
        startPolling(id);
      } else {
        stopPolling();
      }
    } catch (err) {
      console.error("Failed to fetch log analysis detail", err);
    } finally {
      setIsAnalysisLoading(false);
    }
  }, [startPolling, stopPolling]);

  useEffect(() => {
    if (selectedId) {
      fetchAnalysisDetail(selectedId);
    }
    return () => stopPolling();
  }, [selectedId, fetchAnalysisDetail, stopPolling]);

  // Handle File Upload
  const handleFileUpload = async (file: File) => {
    try {
      setIsUploading(true);
      setUploadProgress(10);

      const res = await logService.uploadLog(file, (progressEvent) => {
        if (progressEvent.total) {
          const percent = Math.round((progressEvent.loaded * 90) / progressEvent.total);
          setUploadProgress(percent);
        }
      });

      setUploadProgress(100);
      setSelectedId(res.id);
      await loadHistory();
    } catch (err) {
      console.error("Log upload failed", err);
      alert("Failed to upload log file. Please check file format and server status.");
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDeleteAnalysis = async (id: string) => {
    if (!confirm("Are you sure you want to delete this log analysis record?")) return;
    try {
      await logService.deleteAnalysis(id);
      if (selectedId === id) {
        setSelectedId(null);
        setCurrentAnalysis(null);
      }
      loadHistory();
    } catch (err) {
      console.error("Failed to delete log analysis", err);
    }
  };

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      <PageHeader
        title="AI Log Analyzer"
        subtitle="Upload server logs for automated Google Gemini AI root cause analysis"
        actions={
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={loadHistory}
              className="gap-2 text-xs bg-bg-elevated border-white/[0.08]"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Refresh History
            </Button>
          </div>
        }
      />

      {/* Upload Drag & Drop Zone */}
      <LogUploader
        onUpload={handleFileUpload}
        isUploading={isUploading}
        uploadProgress={uploadProgress}
      />

      {/* Main Content Layout: Grid with History Sidebar & Analysis/Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Analysis History */}
        <div className="lg:col-span-4 space-y-6">
          <AnalysisHistory
            history={history}
            selectedId={selectedId}
            onSelect={(id) => setSelectedId(id)}
            onDelete={handleDeleteAnalysis}
            isLoading={isHistoryLoading}
          />
        </div>

        {/* Right Column: AI Analysis Panel & Log Viewer */}
        <div className="lg:col-span-8 space-y-6">
          {/* AI Analysis Result Panel */}
          <AiAnalysisPanel
            analysis={currentAnalysis}
            isLoading={isAnalysisLoading}
          />

          {/* Syntax Highlighted Log Viewer */}
          {currentAnalysis && currentAnalysis.parsed_entries && (
            <LogViewer
              entries={currentAnalysis.parsed_entries}
              stats={{
                total_lines: currentAnalysis.total_lines,
                error_count: currentAnalysis.error_count,
                warning_count: currentAnalysis.warning_count,
                critical_count: currentAnalysis.critical_count,
                info_count: currentAnalysis.info_count,
              }}
              filename={currentAnalysis.filename}
            />
          )}
        </div>
      </div>
    </div>
  );
}
