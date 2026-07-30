import type { SpendDataPoint, ServiceError, Incident, AiInsight } from "@/types/dashboard";

// 30-day cloud spend
export const spendData: SpendDataPoint[] = Array.from({ length: 30 }, (_, i) => {
  const date = new Date(2026, 6, i + 1);
  const day = date.getDate();
  return {
    date: date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
    compute: Math.round(1400 + Math.sin(i * 0.4) * 300 + Math.random() * 200),
    storage: Math.round(600 + Math.sin(i * 0.3 + 1) * 100 + Math.random() * 80),
    network: Math.round(350 + Math.sin(i * 0.5) * 80 + Math.random() * 60),
    managed: Math.round(500 + Math.cos(i * 0.3) * 120 + Math.random() * 80),
  };
});

// Error rates by service
export const serviceErrors: ServiceError[] = [
  { name: "api-gateway", errorRate: 0.42, requests: 124_800 },
  { name: "auth-service", errorRate: 0.08, requests: 89_400 },
  { name: "payment-svc", errorRate: 0.21, requests: 34_200 },
  { name: "notification", errorRate: 0.65, requests: 18_900 },
  { name: "data-pipeline", errorRate: 0.14, requests: 56_700 },
  { name: "search-svc", errorRate: 0.03, requests: 210_000 },
];

// Active incidents
export const incidents: Incident[] = [
  {
    id: "INC-1042",
    severity: "P0",
    title: "API Gateway elevated 5xx errors in us-east-1",
    service: "api-gateway",
    timeAgo: "4 min ago",
    status: "Investigating",
  },
  {
    id: "INC-1041",
    severity: "P1",
    title: "PostgreSQL replication lag exceeding threshold",
    service: "db-primary",
    timeAgo: "18 min ago",
    status: "Mitigating",
  },
  {
    id: "INC-1040",
    severity: "P2",
    title: "Notification service queue depth above 50k",
    service: "notification",
    timeAgo: "1h 12m ago",
    status: "Investigating",
  },
  {
    id: "INC-1039",
    severity: "P2",
    title: "CDN cache hit ratio degraded in eu-west-1",
    service: "cdn-edge",
    timeAgo: "2h 45m ago",
    status: "Mitigating",
  },
  {
    id: "INC-1038",
    severity: "P3",
    title: "Batch job processing delays in data pipeline",
    service: "data-pipeline",
    timeAgo: "5h 30m ago",
    status: "Resolved",
  },
];

// AI insights
export const aiInsights: AiInsight[] = [
  {
    id: "1",
    category: "Cost",
    text: "14 EC2 instances (r5.2xlarge) in us-east-1 are idle >80% of the time. Right-sizing could save $4,230/month.",
    confidence: 97,
    action: "Apply",
  },
  {
    id: "2",
    category: "Performance",
    text: "api-gateway P95 latency increased 34% over 6h. Root cause likely DB connection pool exhaustion.",
    confidence: 91,
    action: "Investigate",
  },
  {
    id: "3",
    category: "Reliability",
    text: "payment-svc has no cross-region failover configured. Single-region dependency is a reliability risk.",
    confidence: 88,
    action: "Configure",
  },
  {
    id: "4",
    category: "Security",
    text: "3 S3 buckets have public ACLs unintentionally set. These should be reviewed immediately.",
    confidence: 99,
    action: "Review",
  },
  {
    id: "5",
    category: "Cost",
    text: "Reserved Instance coverage is 61%. Purchasing 1-year RIs for steady workloads saves an estimated $12,800/month.",
    confidence: 85,
    action: "Apply",
  },
  {
    id: "6",
    category: "Performance",
    text: "search-svc cache hit rate is 42% — below the 75% target. Consider increasing Redis memory allocation.",
    confidence: 82,
    action: "Optimize",
  },
];

// Donut chart — cost by service
export const costByService = [
  { name: "Compute", value: 38400, fill: "#2563EB" },
  { name: "Storage", value: 14200, fill: "#7C3AED" },
  { name: "Managed DB", value: 18600, fill: "#A855F7" },
  { name: "Networking", value: 8100, fill: "#06B6D4" },
  { name: "Other", value: 4930, fill: "#64748B" },
];

// Health gauge data
export const healthBreakdown = [
  { name: "Compute", value: 99.1, status: "healthy" },
  { name: "Network", value: 97.8, status: "degraded" },
  { name: "Storage", value: 98.9, status: "healthy" },
  { name: "Managed", value: 100, status: "healthy" },
];

// Alert counts (5-min rolling sparkline)
export const alertSparkline = [12, 18, 15, 24, 19, 22, 31, 28, 25, 30, 27, 21, 18, 20, 19, 17, 22, 25, 23, 18, 20, 22, 21, 19, 17, 18, 16, 17, 19, 20];

// Deployment activity
export const deployments = [
  { service: "api-gateway", version: "v2.14.1", deployer: "JD", time: "12 min ago", status: "success" },
  { service: "auth-service", version: "v1.8.3", deployer: "AL", time: "1h 04m ago", status: "success" },
  { service: "payment-svc", version: "v3.2.0", deployer: "MK", time: "2h 38m ago", status: "failed" },
  { service: "search-svc", version: "v5.1.9", deployer: "SR", time: "4h 15m ago", status: "success" },
  { service: "data-pipeline", version: "v0.9.4", deployer: "TW", time: "6h 50m ago", status: "success" },
];
