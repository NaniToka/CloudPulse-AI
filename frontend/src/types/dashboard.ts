export interface KpiMetric {
  label: string;
  value: string;
  subValue?: string;
  trend?: { value: string; direction: "up" | "down" | "neutral"; good?: boolean };
  status?: "healthy" | "warning" | "critical";
}

export interface SpendDataPoint {
  date: string;
  compute: number;
  storage: number;
  network: number;
  managed: number;
}

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

export interface AiInsight {
  id: string;
  category: "Cost" | "Performance" | "Security" | "Reliability";
  text: string;
  confidence: number;
  action: string;
}

export interface TopologyNode {
  id: string;
  name: string;
  type: "lb" | "service" | "database" | "cache" | "queue";
  status: "healthy" | "degraded" | "down";
  latency?: string;
  errorRate?: string;
}
