export type LogLevel = "ERROR" | "WARN" | "WARNING" | "CRITICAL" | "INFO" | "DEBUG" | "UNKNOWN";

export interface ParsedLogEntry {
  line_number: number;
  timestamp?: string | null;
  level: LogLevel | string;
  service?: string | null;
  message: string;
  raw: string;
}

export interface LogStats {
  total_lines: number;
  error_count: number;
  warning_count: number;
  critical_count: number;
  info_count: number;
}

export interface UploadResponse {
  id: string;
  filename: string;
  file_size_bytes: number;
  file_type: "log" | "txt" | "json" | string;
  stats: LogStats;
  status: "pending" | "analyzing" | "complete" | "error";
  created_at: string;
}

export interface LogAnalysis {
  id: string;
  filename: string;
  file_size_bytes: number;
  file_type: string;
  status: "pending" | "analyzing" | "complete" | "error";
  total_lines: number;
  error_count: number;
  warning_count: number;
  critical_count: number;
  info_count: number;
  parsed_entries: ParsedLogEntry[];
  executive_summary?: string | null;
  root_cause?: string | null;
  severity?: "critical" | "high" | "medium" | "low" | string | null;
  recommended_fixes?: string | null;
  preventive_measures?: string | null;
  confidence_score?: number | null;
  ai_error?: string | null;
  created_at: string;
  updated_at?: string;
}

export interface AnalysisListItem {
  id: string;
  filename: string;
  file_size_bytes: number;
  file_type: string;
  status: "pending" | "analyzing" | "complete" | "error";
  total_lines: number;
  error_count: number;
  warning_count: number;
  critical_count: number;
  info_count: number;
  severity?: "critical" | "high" | "medium" | "low" | string | null;
  confidence_score?: number | null;
  executive_summary?: string | null;
  created_at: string;
}

export interface HistoryResponse {
  items: AnalysisListItem[];
  total: number;
}
