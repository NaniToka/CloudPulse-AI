/**
 * Deterministic mock data for the CloudPulse AI dashboard.
 * All values are static so charts look the same on every render.
 */

import type {
  SpendDataPoint,
  ServiceError,
  Incident,
  AiInsight,
  Server,
  Alert,
  CpuDataPoint,
  MemoryDataPoint,
  NetworkDataPoint,
  IncidentTimelinePoint,
  LogEntry,
} from "@/types/dashboard";

// ─── Cloud spend (30 days) ────────────────────────────────────────────────────
export const spendData: SpendDataPoint[] = [
  { date: "Jul 1",  compute: 1520, storage: 610, network: 340, managed: 490 },
  { date: "Jul 2",  compute: 1480, storage: 625, network: 360, managed: 510 },
  { date: "Jul 3",  compute: 1610, storage: 598, network: 320, managed: 530 },
  { date: "Jul 4",  compute: 1390, storage: 640, network: 380, managed: 480 },
  { date: "Jul 5",  compute: 1700, storage: 612, network: 350, managed: 545 },
  { date: "Jul 6",  compute: 1650, storage: 630, network: 370, managed: 520 },
  { date: "Jul 7",  compute: 1580, storage: 618, network: 345, managed: 505 },
  { date: "Jul 8",  compute: 1720, storage: 655, network: 390, managed: 560 },
  { date: "Jul 9",  compute: 1490, storage: 600, network: 330, managed: 495 },
  { date: "Jul 10", compute: 1640, storage: 638, network: 365, managed: 535 },
  { date: "Jul 11", compute: 1760, storage: 670, network: 400, managed: 575 },
  { date: "Jul 12", compute: 1510, storage: 605, network: 325, managed: 500 },
  { date: "Jul 13", compute: 1680, storage: 645, network: 385, managed: 550 },
  { date: "Jul 14", compute: 1590, storage: 622, network: 355, managed: 515 },
  { date: "Jul 15", compute: 1740, storage: 660, network: 395, managed: 565 },
  { date: "Jul 16", compute: 1460, storage: 595, network: 315, managed: 485 },
  { date: "Jul 17", compute: 1630, storage: 635, network: 360, managed: 525 },
  { date: "Jul 18", compute: 1690, storage: 648, network: 375, managed: 540 },
  { date: "Jul 19", compute: 1570, storage: 615, network: 342, managed: 508 },
  { date: "Jul 20", compute: 1800, storage: 675, network: 405, managed: 580 },
  { date: "Jul 21", compute: 1550, storage: 608, network: 335, managed: 498 },
  { date: "Jul 22", compute: 1660, storage: 641, network: 368, managed: 530 },
  { date: "Jul 23", compute: 1710, storage: 658, network: 388, managed: 558 },
  { date: "Jul 24", compute: 1530, storage: 602, network: 328, managed: 492 },
  { date: "Jul 25", compute: 1780, storage: 672, network: 402, managed: 572 },
  { date: "Jul 26", compute: 1620, storage: 632, network: 357, managed: 522 },
  { date: "Jul 27", compute: 1670, storage: 644, network: 372, managed: 537 },
  { date: "Jul 28", compute: 1745, storage: 662, network: 393, managed: 563 },
  { date: "Jul 29", compute: 1595, storage: 619, network: 348, managed: 512 },
  { date: "Jul 30", compute: 1820, storage: 680, network: 410, managed: 585 },
];

// ─── CPU usage (24h, one point per hour) ─────────────────────────────────────
export const cpuData: CpuDataPoint[] = [
  { time: "00:00", web: 32, api: 45, db: 28, worker: 15 },
  { time: "01:00", web: 28, api: 38, db: 25, worker: 12 },
  { time: "02:00", web: 24, api: 32, db: 22, worker: 10 },
  { time: "03:00", web: 22, api: 30, db: 20, worker: 9  },
  { time: "04:00", web: 25, api: 33, db: 23, worker: 11 },
  { time: "05:00", web: 30, api: 40, db: 27, worker: 14 },
  { time: "06:00", web: 42, api: 55, db: 35, worker: 22 },
  { time: "07:00", web: 58, api: 68, db: 44, worker: 35 },
  { time: "08:00", web: 72, api: 80, db: 58, worker: 48 },
  { time: "09:00", web: 78, api: 85, db: 65, worker: 55 },
  { time: "10:00", web: 75, api: 82, db: 62, worker: 52 },
  { time: "11:00", web: 80, api: 88, db: 68, worker: 58 },
  { time: "12:00", web: 85, api: 92, db: 72, worker: 62 },
  { time: "13:00", web: 82, api: 90, db: 70, worker: 60 },
  { time: "14:00", web: 79, api: 86, db: 66, worker: 56 },
  { time: "15:00", web: 83, api: 91, db: 71, worker: 61 },
  { time: "16:00", web: 88, api: 95, db: 75, worker: 65 },
  { time: "17:00", web: 76, api: 83, db: 63, worker: 53 },
  { time: "18:00", web: 65, api: 74, db: 55, worker: 44 },
  { time: "19:00", web: 55, api: 65, db: 48, worker: 36 },
  { time: "20:00", web: 48, api: 58, db: 42, worker: 30 },
  { time: "21:00", web: 42, api: 52, db: 36, worker: 25 },
  { time: "22:00", web: 38, api: 48, db: 32, worker: 20 },
  { time: "23:00", web: 35, api: 44, db: 29, worker: 17 },
];

// ─── Memory usage (24h) ───────────────────────────────────────────────────────
export const memoryData: MemoryDataPoint[] = [
  { time: "00:00", used: 42, cached: 28, free: 30 },
  { time: "01:00", used: 40, cached: 28, free: 32 },
  { time: "02:00", used: 38, cached: 27, free: 35 },
  { time: "03:00", used: 37, cached: 27, free: 36 },
  { time: "04:00", used: 38, cached: 28, free: 34 },
  { time: "05:00", used: 40, cached: 29, free: 31 },
  { time: "06:00", used: 48, cached: 30, free: 22 },
  { time: "07:00", used: 56, cached: 32, free: 12 },
  { time: "08:00", used: 65, cached: 25, free: 10 },
  { time: "09:00", used: 70, cached: 22, free: 8  },
  { time: "10:00", used: 68, cached: 23, free: 9  },
  { time: "11:00", used: 72, cached: 20, free: 8  },
  { time: "12:00", used: 75, cached: 18, free: 7  },
  { time: "13:00", used: 73, cached: 19, free: 8  },
  { time: "14:00", used: 70, cached: 21, free: 9  },
  { time: "15:00", used: 74, cached: 18, free: 8  },
  { time: "16:00", used: 78, cached: 16, free: 6  },
  { time: "17:00", used: 71, cached: 20, free: 9  },
  { time: "18:00", used: 62, cached: 25, free: 13 },
  { time: "19:00", used: 55, cached: 28, free: 17 },
  { time: "20:00", used: 50, cached: 29, free: 21 },
  { time: "21:00", used: 46, cached: 30, free: 24 },
  { time: "22:00", used: 44, cached: 29, free: 27 },
  { time: "23:00", used: 43, cached: 28, free: 29 },
];

// ─── Network traffic (24h, MB/s) ─────────────────────────────────────────────
export const networkData: NetworkDataPoint[] = [
  { time: "00:00", inbound: 120, outbound: 85  },
  { time: "01:00", inbound: 95,  outbound: 70  },
  { time: "02:00", inbound: 80,  outbound: 58  },
  { time: "03:00", inbound: 72,  outbound: 52  },
  { time: "04:00", inbound: 78,  outbound: 56  },
  { time: "05:00", inbound: 95,  outbound: 68  },
  { time: "06:00", inbound: 145, outbound: 102 },
  { time: "07:00", inbound: 210, outbound: 148 },
  { time: "08:00", inbound: 320, outbound: 228 },
  { time: "09:00", inbound: 380, outbound: 268 },
  { time: "10:00", inbound: 360, outbound: 254 },
  { time: "11:00", inbound: 410, outbound: 290 },
  { time: "12:00", inbound: 445, outbound: 315 },
  { time: "13:00", inbound: 425, outbound: 300 },
  { time: "14:00", inbound: 395, outbound: 278 },
  { time: "15:00", inbound: 430, outbound: 304 },
  { time: "16:00", inbound: 468, outbound: 330 },
  { time: "17:00", inbound: 388, outbound: 274 },
  { time: "18:00", inbound: 302, outbound: 212 },
  { time: "19:00", inbound: 248, outbound: 174 },
  { time: "20:00", inbound: 198, outbound: 138 },
  { time: "21:00", inbound: 168, outbound: 118 },
  { time: "22:00", inbound: 145, outbound: 102 },
  { time: "23:00", inbound: 132, outbound: 93  },
];

// ─── Incident timeline (last 7 days) ─────────────────────────────────────────
export const incidentTimeline: IncidentTimelinePoint[] = [
  { day: "Mon", p0: 1, p1: 2, p2: 5, p3: 8  },
  { day: "Tue", p0: 0, p1: 1, p2: 4, p3: 6  },
  { day: "Wed", p0: 2, p1: 3, p2: 7, p3: 10 },
  { day: "Thu", p0: 1, p1: 2, p2: 6, p3: 9  },
  { day: "Fri", p0: 0, p1: 4, p2: 8, p3: 12 },
  { day: "Sat", p0: 0, p1: 1, p2: 3, p3: 5  },
  { day: "Sun", p0: 1, p1: 2, p2: 4, p3: 7  },
];

// ─── Error rates by service ───────────────────────────────────────────────────
export const serviceErrors: ServiceError[] = [
  { name: "api-gateway",   errorRate: 0.42, requests: 124_800 },
  { name: "auth-service",  errorRate: 0.08, requests: 89_400  },
  { name: "payment-svc",   errorRate: 0.21, requests: 34_200  },
  { name: "notification",  errorRate: 0.65, requests: 18_900  },
  { name: "data-pipeline", errorRate: 0.14, requests: 56_700  },
  { name: "search-svc",    errorRate: 0.03, requests: 210_000 },
];

// ─── Servers ──────────────────────────────────────────────────────────────────
export const servers: Server[] = [
  { id: "srv-001", name: "web-prod-01",    type: "EC2",     region: "us-east-1",  status: "healthy",  cpu: 72, memory: 68, uptime: "99.98%", provider: "AWS"   },
  { id: "srv-002", name: "web-prod-02",    type: "EC2",     region: "us-east-1",  status: "healthy",  cpu: 65, memory: 71, uptime: "99.97%", provider: "AWS"   },
  { id: "srv-003", name: "api-prod-01",    type: "GKE Pod", region: "us-central", status: "degraded", cpu: 91, memory: 88, uptime: "99.82%", provider: "GCP"   },
  { id: "srv-004", name: "db-primary",     type: "RDS",     region: "us-east-1",  status: "healthy",  cpu: 48, memory: 75, uptime: "99.99%", provider: "AWS"   },
  { id: "srv-005", name: "db-replica-01",  type: "RDS",     region: "eu-west-1",  status: "healthy",  cpu: 32, memory: 60, uptime: "99.95%", provider: "AWS"   },
  { id: "srv-006", name: "cache-01",       type: "Redis",   region: "us-east-1",  status: "healthy",  cpu: 22, memory: 45, uptime: "100%",   provider: "AWS"   },
  { id: "srv-007", name: "worker-prod-01", type: "VM",      region: "eastus",     status: "healthy",  cpu: 55, memory: 62, uptime: "99.91%", provider: "Azure" },
  { id: "srv-008", name: "worker-prod-02", type: "VM",      region: "eastus",     status: "down",     cpu: 0,  memory: 0,  uptime: "98.40%", provider: "Azure" },
];

// ─── Active incidents ─────────────────────────────────────────────────────────
export const incidents: Incident[] = [
  { id: "INC-1042", severity: "P0", title: "API Gateway elevated 5xx errors in us-east-1",       service: "api-gateway",  timeAgo: "4 min ago",   status: "Investigating" },
  { id: "INC-1041", severity: "P1", title: "PostgreSQL replication lag exceeding threshold",       service: "db-primary",   timeAgo: "18 min ago",  status: "Mitigating"    },
  { id: "INC-1040", severity: "P2", title: "Notification service queue depth above 50k",          service: "notification", timeAgo: "1h 12m ago",  status: "Investigating" },
  { id: "INC-1039", severity: "P2", title: "CDN cache hit ratio degraded in eu-west-1",           service: "cdn-edge",     timeAgo: "2h 45m ago",  status: "Mitigating"    },
  { id: "INC-1038", severity: "P3", title: "Batch job processing delays in data pipeline",        service: "data-pipeline",timeAgo: "5h 30m ago",  status: "Resolved"      },
];

// ─── Active alerts ────────────────────────────────────────────────────────────
export const alerts: Alert[] = [
  { id: "ALT-501", severity: "critical", title: "CPU > 90% on api-prod-01",           service: "api-prod-01",   time: "2 min ago",  status: "active"       },
  { id: "ALT-500", severity: "high",     title: "Memory usage > 85% on web-prod-02",  service: "web-prod-02",   time: "8 min ago",  status: "active"       },
  { id: "ALT-499", severity: "high",     title: "worker-prod-02 is unreachable",       service: "worker-prod-02",time: "12 min ago", status: "active"       },
  { id: "ALT-498", severity: "medium",   title: "Disk usage > 75% on db-primary",     service: "db-primary",    time: "34 min ago", status: "acknowledged" },
  { id: "ALT-497", severity: "medium",   title: "Response time > 2s on /checkout",    service: "payment-svc",   time: "1h ago",     status: "acknowledged" },
  { id: "ALT-496", severity: "low",      title: "Certificate expiring in 14 days",    service: "cdn-edge",      time: "3h ago",     status: "acknowledged" },
  { id: "ALT-495", severity: "low",      title: "Log volume spike on data-pipeline",  service: "data-pipeline", time: "4h ago",     status: "resolved"     },
];

// ─── AI insights ──────────────────────────────────────────────────────────────
export const aiInsights: AiInsight[] = [
  { id: "1", category: "Cost",        confidence: 97, action: "Apply",      text: "14 EC2 instances (r5.2xlarge) in us-east-1 are idle >80% of the time. Right-sizing could save $4,230/month."                          },
  { id: "2", category: "Performance", confidence: 91, action: "Investigate",text: "api-gateway P95 latency increased 34% over 6h. Root cause likely DB connection pool exhaustion."                                      },
  { id: "3", category: "Reliability", confidence: 88, action: "Configure",  text: "payment-svc has no cross-region failover configured. Single-region dependency is a reliability risk."                                 },
  { id: "4", category: "Security",    confidence: 99, action: "Review",     text: "3 S3 buckets have public ACLs unintentionally set. These should be reviewed immediately."                                             },
  { id: "5", category: "Cost",        confidence: 85, action: "Apply",      text: "Reserved Instance coverage is 61%. Purchasing 1-year RIs for steady workloads saves an estimated $12,800/month."                      },
  { id: "6", category: "Performance", confidence: 82, action: "Optimize",   text: "search-svc cache hit rate is 42% — below the 75% target. Consider increasing Redis memory allocation."                               },
];

// ─── Cost by service (donut) ──────────────────────────────────────────────────
export const costByService = [
  { name: "Compute",    value: 38400, fill: "#2563EB" },
  { name: "Storage",    value: 14200, fill: "#7C3AED" },
  { name: "Managed DB", value: 18600, fill: "#A855F7" },
  { name: "Networking", value: 8100,  fill: "#06B6D4" },
  { name: "Other",      value: 4930,  fill: "#64748B" },
];

// ─── Health breakdown ─────────────────────────────────────────────────────────
export const healthBreakdown = [
  { name: "Compute", value: 99.1, status: "healthy"  },
  { name: "Network", value: 97.8, status: "degraded" },
  { name: "Storage", value: 98.9, status: "healthy"  },
  { name: "Managed", value: 100,  status: "healthy"  },
];

// ─── Deployments ─────────────────────────────────────────────────────────────
export const deployments = [
  { service: "api-gateway",   version: "v2.14.1", deployer: "JD", time: "12 min ago",  status: "success" },
  { service: "auth-service",  version: "v1.8.3",  deployer: "AL", time: "1h 04m ago",  status: "success" },
  { service: "payment-svc",   version: "v3.2.0",  deployer: "MK", time: "2h 38m ago",  status: "failed"  },
  { service: "search-svc",    version: "v5.1.9",  deployer: "SR", time: "4h 15m ago",  status: "success" },
  { service: "data-pipeline", version: "v0.9.4",  deployer: "TW", time: "6h 50m ago",  status: "success" },
];

// ─── Log entries ──────────────────────────────────────────────────────────────
export const logEntries: LogEntry[] = [
  { id: "1",  timestamp: "2026-07-30 14:32:01", level: "ERROR", service: "api-gateway",   message: "Connection pool exhausted: max_connections=100 exceeded",                       traceId: "a1b2c3d4" },
  { id: "2",  timestamp: "2026-07-30 14:31:58", level: "WARN",  service: "db-primary",    message: "Replication lag detected: 2847ms behind primary",                              traceId: "e5f6g7h8" },
  { id: "3",  timestamp: "2026-07-30 14:31:45", level: "ERROR", service: "payment-svc",   message: "Stripe webhook timeout after 30s for event evt_3NqX2K2eZvKYlo2C1234",         traceId: "i9j0k1l2" },
  { id: "4",  timestamp: "2026-07-30 14:31:30", level: "INFO",  service: "auth-service",  message: "User session created: user_id=7f4a9b12 ip=192.168.1.42",                      traceId: "m3n4o5p6" },
  { id: "5",  timestamp: "2026-07-30 14:31:22", level: "WARN",  service: "notification",  message: "Queue depth threshold exceeded: current=52341 threshold=50000",               traceId: "q7r8s9t0" },
  { id: "6",  timestamp: "2026-07-30 14:31:15", level: "ERROR", service: "api-gateway",   message: "HTTP 503 returned for GET /api/v2/products: upstream timeout",                traceId: "u1v2w3x4" },
  { id: "7",  timestamp: "2026-07-30 14:31:02", level: "INFO",  service: "search-svc",    message: "Index refresh completed in 1240ms, 2.4M documents indexed",                   traceId: "y5z6a7b8" },
  { id: "8",  timestamp: "2026-07-30 14:30:55", level: "DEBUG", service: "worker-prod-01",message: "Batch job batch_20260730_143 started: 14,200 records to process",            traceId: "c9d0e1f2" },
  { id: "9",  timestamp: "2026-07-30 14:30:41", level: "ERROR", service: "worker-prod-02",message: "Health check failed: connection refused on :8080 after 3 retries",            traceId: "g3h4i5j6" },
  { id: "10", timestamp: "2026-07-30 14:30:28", level: "WARN",  service: "cache-01",      message: "Redis eviction rate high: 14,200 keys evicted in last 60s",                  traceId: "k7l8m9n0" },
];
