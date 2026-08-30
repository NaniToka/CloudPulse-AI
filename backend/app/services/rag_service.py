"""
RAG Pipeline Service — Manages RAG telemetry indexing, retrieval, and Gemini API synthesis.
"""

import json
import uuid

import structlog

from app.core.config import settings
from app.schemas.rag_chat import (
    RAGQueryRequest,
    RAGQueryResponse,
    RelatedItem,
    SourceCitation,
)
from app.services.vector_store_service import vector_store_service

log = structlog.get_logger(__name__)

RAG_SYSTEM_PROMPT = """You are CloudPulse AI Infrastructure RAG Assistant.
You answer questions about the user's cloud infrastructure using ONLY the retrieved telemetry context provided.
Provide clear markdown explanations, technical evidence, and actionable recommendations.

Always return a valid JSON object matching EXACTLY this structure:
{
  "answer": "Detailed markdown explanation based on retrieved infrastructure context.",
  "confidence_score": 0.95,
  "evidence_sources": [
    {
      "collection": "metrics",
      "title": "CPU & Memory Heap Saturation Telemetry",
      "snippet": "CPU utilization on api-gateway reached 94.2% in us-east-1.",
      "relevance_score": 0.96
    }
  ],
  "related_alerts": [
    {
      "type": "alert",
      "id": "alt-9482",
      "title": "Critical CPU Saturation Warning on api-gateway",
      "severity": "Critical"
    }
  ],
  "related_traces": [
    {
      "type": "trace",
      "id": "tr-94821a0b",
      "title": "POST /api/v1/checkout",
      "status": "error"
    }
  ],
  "related_incidents": [
    {
      "type": "incident",
      "id": "inc-4029",
      "title": "Database Connection Pool Exhaustion on auth-service",
      "status": "Investigating"
    }
  ],
  "recommended_actions": [
    "Scale api-gateway container replicas from 4 to 12 instances",
    "Increase PgBouncer connection pool max_connections to 400"
  ],
  "suggested_followup_questions": [
    "Which service is consuming the most memory right now?",
    "Show me the latency waterfall for the slowest trace."
  ]
}
"""


def seed_infrastructure_rag_data() -> None:
    """Pre-populates vector collections with live telemetry context."""
    sample_docs = [
        # Metrics collection
        {
            "collection": "metrics",
            "id": "doc-met-101",
            "text": "CPU Utilization on api-gateway (us-east-1) reached 94.2% alongside Memory Heap at 7.8GB/8.0GB (+450MB/15m leak rate). P99 latency increased to 2,840ms.",
            "metadata": {"service": "api-gateway", "metric": "cpu_usage", "value": "94.2%"},
        },
        {
            "collection": "metrics",
            "id": "doc-met-102",
            "text": "PostgreSQL Database Connection Pool on auth-service reached 198 active connections out of max 200 limit due to bcrypt password hashing queue locking.",
            "metadata": {"service": "auth-service", "metric": "db_connections", "value": "198/200"},
        },
        # Incidents collection
        {
            "collection": "incidents",
            "id": "doc-inc-201",
            "text": "INC-4029: Critical Database Connection Pool Exhaustion on auth-service (Severity: P0). Status: Investigating. Assigned to SRE Team.",
            "metadata": {"incident_id": "INC-4029", "severity": "P0", "service": "auth-service"},
        },
        {
            "collection": "incidents",
            "id": "doc-inc-202",
            "text": "INC-3882: API Gateway High Error Rate & 504 Timeout Surge (Severity: P1). Resolved via Horizontal Pod Autoscaler replica count increase.",
            "metadata": {"incident_id": "INC-3882", "severity": "P1", "service": "api-gateway"},
        },
        # Traces collection
        {
            "collection": "traces",
            "id": "doc-tr-301",
            "text": "Trace tr-94821a0b (POST /api/v1/checkout) total duration 654.5ms with status ERROR. Bottleneck: external Stripe API call taking 420ms (64% of request duration).",
            "metadata": {
                "trace_id": "tr-94821a0b",
                "slowest_service": "external-payment-api",
                "duration_ms": 654.5,
            },
        },
        # Costs collection
        {
            "collection": "ai_reports",
            "id": "doc-cost-401",
            "text": "FinOps Cloud Cost Summary: Total monthly cloud spend $14,250. Highest cost resource: db.r6g.4xlarge PostgreSQL Aurora Cluster ($4,820/mo, 33.8% of total bill). Optimization potential: $3,180/mo savings.",
            "metadata": {
                "domain": "cloud_cost",
                "highest_cost_resource": "PostgreSQL Aurora Cluster",
                "monthly_spend": 14250,
            },
        },
        # Alerts collection
        {
            "collection": "alerts",
            "id": "doc-alt-501",
            "text": "Alert ALT-9482: High CPU Saturation Warning on api-gateway (>85% for 15 minutes). Triggered automatically by monitoring rule.",
            "metadata": {"alert_id": "ALT-9482", "severity": "Critical", "service": "api-gateway"},
        },
    ]

    for d in sample_docs:
        vector_store_service.add_document(
            collection_name=d["collection"],
            doc_id=d["id"],
            text=d["text"],
            metadata=d["metadata"],
        )


class RAGService:
    """RAG Service conducting context retrieval and Gemini answer synthesis."""

    def __init__(self) -> None:
        seed_infrastructure_rag_data()

    async def answer_question(self, req: RAGQueryRequest) -> RAGQueryResponse:
        """Executes RAG pipeline: Retrieves context from vector collections -> Synthesizes answer using Gemini."""
        conv_id = req.conversation_id or f"conv-{uuid.uuid4().hex[:8]}"

        # Step 1: Semantic Retrieval over ChromaDB collections
        retrieved_docs = vector_store_service.query_similarity(
            query=req.question,
            collection_filter=req.collection_filter,
            top_k=5,
        )

        # Step 2: Build Evidence Sources
        sources: list[SourceCitation] = []
        context_snippets = []

        for doc in retrieved_docs:
            sources.append(
                SourceCitation(
                    collection=doc["collection"],
                    title=f"Telemetry {doc['collection'].upper()} Record ({doc['id']})",
                    snippet=doc["text"],
                    relevance_score=doc.get("score", 0.92),
                    metadata=doc.get("metadata", {}),
                )
            )
            context_snippets.append(f"[{doc['collection'].upper()}]: {doc['text']}")

        # Step 3: Invoke Gemini API if configured
        import time
        from app.services.metrics_collector import metrics_collector
        start_ai = time.perf_counter()

        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY not in ("your_key_here", ""):
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(
                    model_name=settings.GEMINI_MODEL,
                    system_instruction=RAG_SYSTEM_PROMPT,
                    generation_config={
                        "temperature": 0.2,
                        "response_mime_type": "application/json",
                    },
                )

                user_prompt = (
                    f"Answer User Infrastructure Question:\n"
                    f"- User Question: {req.question}\n"
                    f"- Retrieved Telemetry Context:\n" + "\n".join(context_snippets)
                )

                response = await model.generate_content_async(user_prompt)
                data = json.loads(response.text.strip())

                res = RAGQueryResponse(
                    conversation_id=conv_id,
                    question=req.question,
                    answer=data.get(
                        "answer",
                        "Based on telemetry context, CPU saturation is caused by memory heap leak on api-gateway.",
                    ),
                    provider="LIVE AI (Gemini 1.5 Pro)",
                    evidence_sources=sources,
                    confidence_score=float(data.get("confidence_score", 0.95)),
                    related_alerts=[RelatedItem(**a) for a in data.get("related_alerts", [])],
                    related_traces=[RelatedItem(**t) for t in data.get("related_traces", [])],
                    related_incidents=[RelatedItem(**i) for i in data.get("related_incidents", [])],
                    recommended_actions=data.get("recommended_actions", []),
                    suggested_followup_questions=data.get("suggested_followup_questions", []),
                )
                duration_ai = time.perf_counter() - start_ai
                metrics_collector.record_ai_execution(
                    provider="google_gemini_rag",
                    model=settings.GEMINI_MODEL,
                    duration_sec=duration_ai,
                    success=True,
                    fallback_used=False,
                    tokens_est=(len(user_prompt) + len(response.text)) // 4,
                )
                from app.crud.crud_rag_chat import crud_rag_chat

                await crud_rag_chat.add_message(
                    conv_id, res.question, res.answer, res.confidence_score
                )
                log.info("rag_query_completed_live_ai", conversation_id=conv_id, sources_count=len(sources))
                return res
            except Exception as exc:
                duration_ai = time.perf_counter() - start_ai
                metrics_collector.record_ai_execution(
                    provider="google_gemini_rag",
                    model=settings.GEMINI_MODEL,
                    duration_sec=duration_ai,
                    success=False,
                    fallback_used=True,
                )
                log.warning("gemini_rag_query_failed_falling_back", error=str(exc))

        # Fallback RAG synthesis if Gemini API unconfigured or offline
        log.info("rag_query_using_local_demo_provider", conversation_id=conv_id, question=req.question[:60])
        res = self._generate_fallback_rag_response(conv_id, req.question, sources)
        duration_ai = time.perf_counter() - start_ai
        metrics_collector.record_ai_execution(
            provider="local_fallback_rag",
            model="deterministic_rag",
            duration_sec=duration_ai,
            success=True,
            fallback_used=True,
            tokens_est=(len(req.question) + len(res.answer)) // 4,
        )
        from app.crud.crud_rag_chat import crud_rag_chat

        await crud_rag_chat.add_message(conv_id, res.question, res.answer, res.confidence_score)
        return res

    def _generate_fallback_rag_response(
        self, conversation_id: str, question: str, sources: list[SourceCitation]
    ) -> RAGQueryResponse:
        q_lower = question.lower()

        if any(k in q_lower for k in ["cpu", "high", "unhealthy", "load", "memory", "oom"]):
            answer = (
                "### Infrastructure Diagnostics: Telemetry & Resource Utilization\n\n"
                "CloudPulse AI analyzed live metrics and detected **CPU utilization at 94.2%** and **Memory at 88.7%** on `api-gateway` in region `us-east-1`.\n\n"
                "#### Root Cause:\n"
                "- Unbounded memory heap growth (+450MB/15m) in session handler during traffic burst.\n"
                "- Thread pool lock contention resulting in elevated P99 latency and HTTP 504 Gateway Timeouts.\n\n"
                "#### Recommended Actions:\n"
                "1. Scale container replicas for `api-gateway` from 4 to 12 instances.\n"
                "2. Flush stale session memory cache entries in Redis cluster.\n"
                "3. Enable Horizontal Pod Autoscaling (HPA) target at 75% CPU."
            )
            rel_alerts = [
                RelatedItem(
                    type="alert",
                    id="ALT-9482",
                    title="Critical CPU Saturation on api-gateway",
                    severity="Critical",
                )
            ]
            rel_traces = [
                RelatedItem(
                    type="trace", id="tr-94821a0b", title="POST /api/v1/checkout", status="error"
                )
            ]
            rel_incidents = [
                RelatedItem(
                    type="incident",
                    id="INC-4029",
                    title="Database Connection Pool Exhaustion on auth-service",
                    status="Investigating",
                )
            ]
            actions = [
                "Scale api-gateway pod replicas from 4 to 12",
                "Flush stale session memory cache in Redis",
            ]
            followups = [
                "Which service is consuming the most memory right now?",
                "Show me the latency waterfall for the slowest trace.",
            ]

        elif any(k in q_lower for k in ["cost", "spend", "bill", "saving", "price", "budget", "finops"]):
            answer = (
                "### Cloud Cost & FinOps Optimization Summary\n\n"
                "Your total monthly cloud infrastructure spend across all clouds is **$14,250/mo**.\n\n"
                "#### Highest Cost Resources:\n"
                "- **PostgreSQL Aurora Cluster (`db.r6g.4xlarge`)**: **$4,820/mo** (33.8% of AWS bill).\n"
                "- **Unattached EBS Volumes (14 volumes)**: **$840/mo** (idle storage waste).\n"
                "- **Overprovisioned Kubernetes Nodes**: **$2,340/mo** (average CPU utilization < 18%).\n\n"
                "#### Potential Monthly Savings:\n"
                "- Purchasing 1-Year Compute Savings Plans: **$3,180/mo**.\n"
                "- Deleting unattached EBS volumes & snapshots: **$840/mo**.\n"
                "- Downsizing idle worker nodes: **$1,120/mo**."
            )
            rel_alerts = []
            rel_traces = []
            rel_incidents = []
            actions = [
                "Purchase 1-Year Savings Plan for Aurora Cluster",
                "Delete 14 unattached EBS volumes",
                "Apply node rightsizing recommendations",
            ]
            followups = [
                "How much can we save by purchasing Reserved Instances?",
                "Show all idle EC2 instances across AWS and GCP.",
            ]

        elif any(k in q_lower for k in ["latency", "slow", "trace", "duration", "timeout", "p99", "bottleneck"]):
            answer = (
                "### Distributed Tracing & Latency Bottleneck Analysis\n\n"
                "The slowest service in your architecture is **`billing-service -> Stripe API Gateway`**.\n\n"
                "#### Key Metrics:\n"
                "- **Trace ID**: `tr-94821a0b` (`POST /api/v1/checkout`)\n"
                "- **Total Request Duration**: `654.5 ms` (P99 threshold: 300ms)\n"
                "- **Stripe API Call Span**: `420.0 ms` (64% of total trace duration)\n"
                "- **PostgreSQL Transaction Lock**: `148.0 ms`\n\n"
                "#### Recommendation:\n"
                "Offload synchronous payment verification to an asynchronous Kafka/Celery event queue and apply connection pooling."
            )
            rel_alerts = []
            rel_traces = [
                RelatedItem(
                    type="trace", id="tr-94821a0b", title="POST /api/v1/checkout", status="error"
                )
            ]
            rel_incidents = []
            actions = [
                "Wrap Stripe API HTTP calls in async background queue",
                "Add Redis caching for user authorization tokens",
            ]
            followups = [
                "Why is the Stripe API span taking 420ms?",
                "Show me the service dependency map for billing-service.",
            ]

        elif any(k in q_lower for k in ["incident", "outage", "alert", "error", "down", "failure"]):
            answer = (
                "### Incident Intelligence & Correlated Signals\n\n"
                "There is currently **1 active P0 Critical incident** requiring immediate attention:\n\n"
                "- **Incident**: `P99 Latency degradation on Payment API` (`payment-service`)\n"
                "- **Root Cause**: Redis memory limit reached maxmemory threshold (2GB), evicting session tokens.\n"
                "- **Impact**: 8.4% drop in checkout conversion rate.\n"
                "- **Confidence Score**: 96%\n\n"
                "#### Auto-Remediation Plan:\n"
                "1. Scale Redis Cluster Memory to 8GB (`wf-redis-scale`).\n"
                "2. Run UNLINK on expired telemetry namespaces."
            )
            rel_alerts = [
                RelatedItem(
                    type="alert",
                    id="ALT-9482",
                    title="Redis Memory Limit Breached (99.4%)",
                    severity="Critical",
                )
            ]
            rel_traces = [
                RelatedItem(
                    type="trace", id="tr-94821a0b", title="POST /api/v1/checkout", status="error"
                )
            ]
            rel_incidents = [
                RelatedItem(
                    type="incident",
                    id="INC-4029",
                    title="P99 Latency degradation on Payment API",
                    status="Investigating",
                    severity="CRITICAL",
                )
            ]
            actions = [
                "Execute remediation workflow wf-redis-scale",
                "Notify #sre-oncall Slack channel",
            ]
            followups = [
                "What is the blast radius for INC-4029?",
                "Show evidence logs for the payment-service outage.",
            ]

        elif any(k in q_lower for k in ["k8s", "kubernetes", "pod", "cluster", "node", "deployment"]):
            answer = (
                "### Kubernetes Container Intelligence\n\n"
                "CloudPulse AI is monitoring **3 clusters (48 nodes, 284 pods)** across GKE and EKS.\n\n"
                "- **Cluster Health**: `gke-prod-us-east1` (Healthy), `eks-prod-eu-west1` (Degraded)\n"
                "- **CrashLoopBackOff**: 2 pods detected on namespace `payments` (`payment-worker-v2`)\n"
                "- **Resource Efficiency**: Cluster CPU allocation 42%, Memory allocation 68%\n\n"
                "#### Root Cause:\n"
                "Missing environment secret `STRIPE_WEBHOOK_SECRET` in `payment-worker-v2` deployment spec."
            )
            rel_alerts = [
                RelatedItem(
                    type="alert",
                    id="ALT-K8S-01",
                    title="Pod CrashLoopBackOff: payment-worker-v2",
                    severity="High",
                )
            ]
            rel_traces = []
            rel_incidents = []
            actions = [
                "Inject missing secret into payments namespace",
                "Restart payment-worker-v2 deployment rollouts",
            ]
            followups = [
                "Show pod logs for payment-worker-v2.",
                "List all pods in CrashLoopBackOff state.",
            ]

        elif any(k in q_lower for k in ["security", "cve", "vulnerability", "iam", "compliance", "policy"]):
            answer = (
                "### AI Security & Cloud Compliance Overview\n\n"
                "Overall Cloud Security Posture Score: **88 / 100 (SOC2 & ISO 27001 Compliant)**.\n\n"
                "- **Critical Findings**: 0\n"
                "- **High Findings**: 2 (S3 bucket public read permissions on `media-assets-prod`, unrotated IAM access keys > 90 days)\n"
                "- **Medium Findings**: 5 (Security group 0.0.0.0/0 on SSH port 22)\n\n"
                "#### Remediation Actions:\n"
                "1. Apply S3 Block Public Access on `media-assets-prod`.\n"
                "2. Rotate IAM credentials for user `ci-deployer-bot`."
            )
            rel_alerts = []
            rel_traces = []
            rel_incidents = []
            actions = [
                "Enforce S3 Block Public Access",
                "Rotate CI/CD IAM credentials",
            ]
            followups = [
                "Run a fresh CSPM security scan on AWS.",
                "Show compliance breakdown for SOC2.",
            ]

        else:
            answer = (
                "### CloudPulse AI System Health Overview\n\n"
                "Overall infrastructure health is **STABLE (96.1% healthy)** across AWS, GCP, and Azure.\n\n"
                "- **Monitored Compute Nodes**: 2,847 active servers\n"
                "- **Avg Ingress Latency**: 124.0 ms (P99: 248.0 ms)\n"
                "- **Active Correlated Incidents**: 1 P0 Critical, 1 P1 High\n"
                "- **Monthly Cloud Spend**: $84,230 (Potential savings: $18,400/mo)\n"
                "- **AI Anomaly Detection Pipeline**: Operational with 0 ingestion lag."
            )
            rel_alerts = [
                RelatedItem(
                    type="alert",
                    id="ALT-9482",
                    title="High CPU Saturation Warning on api-gateway",
                    severity="Warning",
                )
            ]
            rel_traces = []
            rel_incidents = [
                RelatedItem(
                    type="incident",
                    id="INC-4029",
                    title="P99 Latency degradation on Payment API",
                    status="Investigating",
                    severity="CRITICAL",
                )
            ]
            actions = [
                "Review active P0 incident in Incident Command Center",
                "Run cost optimization sweep on unattached EBS storage",
            ]
            followups = [
                "Why is CPU utilization high on api-gateway?",
                "What are our top 3 cloud cost savings opportunities?",
                "Show active incidents and MTTR metrics.",
            ]

        return RAGQueryResponse(
            conversation_id=conversation_id,
            question=question,
            answer=answer,
            provider="LOCAL DEMO AI (Deterministic RAG)",
            evidence_sources=sources,
            confidence_score=0.94,
            related_alerts=rel_alerts,
            related_traces=rel_traces,
            related_incidents=rel_incidents,
            recommended_actions=actions,
            suggested_followup_questions=followups,
        )


rag_service = RAGService()

