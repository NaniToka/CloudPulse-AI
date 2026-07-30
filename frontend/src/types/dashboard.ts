// ─── Chart data points ────────────────────────────────────────────────────────

export interface SpendDataPoint {
  date: string;
  compute: number;
  storage: number;
  network: number;
  managed: number;
}

export interface CpuDataPoint {
  time: string;
  web: number;
  api: number;
  db: number;
  worker: number;
}

export interface MemoryDataPoint {
  time: string;
  used: number;
  cached: number;
  free: number;
}

export interface NetworkDataPoint {
  time: string;
  inbound: number;
  outbound: number;
}

export interface IncidentTimelinePoint {
  day: string;
  p0: number;
  p1: number;
  p2: number;
  p3: number;
}

// ─── Domain entities ──────────────────────────────────────────────────────────

export interface ServiceError {
  name: string;
  errorRate: number;
  requests: number;
}

export interface Incident {
  id: string;
  severity: "P0" | "P1" | "P2" | "P3";
  title: string;
  service: string;
  timeAgo: string;
  status: "Investigating" | "Mitigating" | "Resolved" | "Open";
}

export interface Alert {
  id: string;
  severity: "critical" | "high" | "medium" | "low";
  title: string;
  service: string;
  time: string;
  status: "active" | "acknowledged" | "resolved";
}

export interface Server {
  id: string;
  name: string;
  type: string;
  region: string;
  status: "healthy" | "degraded" | "down";
  cpu: number;
  memory: number;
  uptime: string;
  provider: "AWS" | "GCP" | "Azure";
}

export interface AiInsight {
  id: string;
  category: "Cost" | "Performance" | "Security" | "Reliability";
  text: string;
  confidence: number;
  action: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: "ERROR" | "WARN" | "INFO" | "DEBUG";
  service: string;
  message: string;
  traceId: string;
}
