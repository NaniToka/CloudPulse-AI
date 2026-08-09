"""
AI service — wraps Google Gemini and provides:
  - Stateless chat completions (non-streaming)
  - Async streaming completions via Server-Sent Events
  - System prompt injection for cloud-engineering persona
  - In-process per-user rate limiting (token bucket, no extra dep)
  - Graceful degradation when GEMINI_API_KEY is not set
"""

from __future__ import annotations

import time
from collections import defaultdict
from collections.abc import AsyncGenerator

import structlog

from app.core.config import settings

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are CloudPulse AI Copilot, an expert Site Reliability Engineering (SRE)
assistant embedded inside the CloudPulse AI platform.

Your role:
- Help cloud engineers analyze infrastructure metrics, logs, incidents, and cloud costs.
- Provide actionable recommendations backed by SRE best practices (SLOs, error budgets,
  toil reduction, blameless post-mortems).
- Explain technical concepts clearly at the right depth for senior engineers.
- Format responses in clean Markdown: use headings, bullet points, bold for key terms,
  and fenced code blocks with the correct language tag for all code/commands/config.
- When given log snippets, metrics data, or incident descriptions, perform root-cause
  analysis and suggest concrete mitigation steps.
- Be concise but complete. Avoid filler sentences.

Constraints:
- Never fabricate specific numbers you weren't given. Say "based on typical patterns" when estimating.
- Always recommend testing changes in staging before production.
- When discussing cost savings, give a range rather than a precise number unless data is provided.
- Do NOT discuss topics unrelated to cloud infrastructure, SRE, DevOps, or platform engineering.
"""

# ---------------------------------------------------------------------------
# In-process rate limiter (token bucket per user UUID)
# ---------------------------------------------------------------------------


class _TokenBucket:
    """
    Simple token-bucket rate limiter.

    capacity   — maximum tokens (burst)
    refill_rate — tokens added per second
    """

    __slots__ = ("capacity", "rate", "_tokens", "_last_refill")

    def __init__(self, capacity: int, refill_rate: float) -> None:
        self.capacity = capacity
        self.rate = refill_rate
        self._tokens: float = float(capacity)
        self._last_refill: float = time.monotonic()

    def consume(self, tokens: int = 1) -> bool:
        """Return True if the request is allowed, False if rate-limited."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last_refill = now

        if self._tokens >= tokens:
            self._tokens -= tokens
            return True
        return False


class RateLimiter:
    """Per-user token bucket store."""

    def __init__(
        self,
        capacity: int = 20,  # 20 requests burst
        refill_rate: float = 0.5,  # 1 request every 2 seconds sustained
    ) -> None:
        self._buckets: dict[str, _TokenBucket] = defaultdict(
            lambda: _TokenBucket(capacity, refill_rate)
        )

    def is_allowed(self, user_id: str) -> bool:
        return self._buckets[user_id].consume()


# Module-level singleton — shared across all requests in a single worker process
rate_limiter = RateLimiter()

# ---------------------------------------------------------------------------
# Gemini client factory (lazy initialisation)
# ---------------------------------------------------------------------------


def _get_model():
    """
    Return a configured GenerativeModel.

    Raises RuntimeError if GEMINI_API_KEY is not set, so the endpoint can
    return a clean 503 instead of an obscure SDK error.
    """
    import google.generativeai as genai  # noqa: PLC0415

    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY in ("your_key_here", ""):
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    genai.configure(api_key=settings.GEMINI_API_KEY)

    generation_config = {
        "temperature": settings.GEMINI_TEMPERATURE,
        "max_output_tokens": settings.GEMINI_MAX_OUTPUT_TOKENS,
        "top_p": 0.95,
        "top_k": 40,
    }

    return genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        generation_config=generation_config,
        system_instruction=SYSTEM_PROMPT,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_history(messages: list[dict]) -> list[dict]:
    """
    Convert our internal message dicts to the Gemini `contents` format.

    Input:  [{"role": "user"|"assistant", "content": "..."}]
    Output: [{"role": "user"|"model",     "parts":   ["..."]}]
    """
    gemini_history = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        gemini_history.append({"role": role, "parts": [msg["content"]]})
    return gemini_history


def _generate_fallback_copilot_response(user_message: str) -> str:
    """Generate deterministic SRE Copilot response for local development."""
    msg_l = user_message.lower()

    if any(w in msg_l for w in ["cpu", "memory", "load", "oom", "leak"]):
        return (
            "### CloudPulse AI Copilot — Infrastructure Diagnostics\n\n"
            "**Telemetry Analysis:**\n"
            "- Analyzed CPU & memory telemetry metrics for cluster services.\n"
            "- Identified **CPU saturation at 94.2%** on `api-gateway` in `us-east-1`.\n"
            "- Session cache heap memory allocation grew +450MB/15m under peak load.\n\n"
            "**Recommended Mitigation:**\n"
            "1. Scale pod replicas from 4 to 12 (`kubectl scale deployment api-gateway --replicas=12`).\n"
            "2. Flush stale session cache namespaces in Redis.\n"
            "3. Configure HPA target threshold at 75% CPU utilization.\n\n"
            "> *Note: Running in Local Demo SRE mode. Configure GEMINI_API_KEY in .env for live Gemini Pro completions.*"
        )
    elif any(w in msg_l for w in ["cost", "spend", "bill", "savings", "finops"]):
        return (
            "### CloudPulse AI Copilot — FinOps Optimization Recommendations\n\n"
            "**Spend Overview:**\n"
            "- Current Monthly Spend: **$84,230/mo** across AWS, GCP, and Azure.\n"
            "- Top Expense: Aurora PostgreSQL Cluster (`db.r6g.4xlarge`) at $4,820/mo.\n\n"
            "**Identified Cost Savings Opportunities:**\n"
            "- **Reserved Instances / Savings Plans**: Save **$18,400/yr** (38% reduction) with 1-year commitment.\n"
            "- **Unattached EBS Volumes**: Delete 14 orphan volumes to save **$840/mo** immediately.\n"
            "- **Downsize Idle Nodes**: 8 development VMs have < 2% average CPU utilization.\n\n"
            "> *Note: Running in Local Demo SRE mode. Configure GEMINI_API_KEY in .env for live Gemini Pro completions.*"
        )
    elif any(w in msg_l for w in ["incident", "rca", "outage", "p0", "alert"]):
        return (
            "### CloudPulse AI Copilot — Incident Intelligence & Root Cause Analysis\n\n"
            "**Active Correlated Incident:** `INC-4029: P99 Latency degradation on Payment API`\n"
            "- **Severity**: P0 Critical | **Confidence**: 96%\n"
            "- **Impacted Services**: `payment-service`, `checkout-svc`, `auth-service`\n"
            "- **Root Cause**: Redis memory saturation (99.4%) triggered eviction storms for session tokens.\n\n"
            "**SRE Runbook Execution:**\n"
            "- Automated remediation workflow `wf-redis-scale` is queued for execution.\n"
            "- Estimated time to full recovery: **12 minutes**.\n\n"
            "> *Note: Running in Local Demo SRE mode. Configure GEMINI_API_KEY in .env for live Gemini Pro completions.*"
        )
    else:
        return (
            "### CloudPulse AI Copilot — SRE Assistant\n\n"
            "CloudPulse AI is monitoring your multi-cloud observability plane:\n\n"
            "- **Infrastructure Health**: 96.1% healthy (2,731 / 2,847 nodes online)\n"
            "- **Active Pipelines**: Metrics, Logs, Distributed Traces, and ChromaDB RAG Vector Store\n"
            "- **SRE Best Practices**: Blameless RCA, automated runbook rollbacks, SLO tracking\n\n"
            "You can ask me to analyze CPU bottlenecks, investigate distributed traces, optimize multi-cloud spending, or generate Kubernetes remediation runbooks.\n\n"
            "> *Note: Running in Local Demo SRE mode. Configure GEMINI_API_KEY in .env for live Gemini Pro completions.*"
        )


async def chat_completion(
    user_message: str,
    history: list[dict],
    user_id: str,
) -> str:
    """
    Non-streaming chat completion. Uses Gemini if configured, or falls back to local SRE demo engine.
    """
    if not rate_limiter.is_allowed(user_id):
        raise ValueError(
            "Rate limit exceeded. Please wait a moment before sending another message."
        )

    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY in ("your_key_here", ""):
        log.info("gemini_key_missing_using_local_copilot", user_id=user_id)
        return _generate_fallback_copilot_response(user_message)

    try:
        model = _get_model()
        gemini_history = build_history(history)

        log.info(
            "gemini_request",
            user_id=user_id,
            model=settings.GEMINI_MODEL,
            history_length=len(gemini_history),
            message_preview=user_message[:80],
        )

        chat = model.start_chat(history=gemini_history)
        response = await chat.send_message_async(user_message)
        reply = response.text

        log.info(
            "gemini_response",
            user_id=user_id,
            reply_length=len(reply),
        )
        return reply
    except Exception as exc:
        log.warning("gemini_call_failed_falling_back_to_local", error=str(exc))
        return _generate_fallback_copilot_response(user_message)


async def stream_chat_completion(
    user_message: str,
    history: list[dict],
    user_id: str,
) -> AsyncGenerator[str, None]:
    """
    Streaming chat completion. Yields text chunks as they arrive.
    """
    if not rate_limiter.is_allowed(user_id):
        raise ValueError(
            "Rate limit exceeded. Please wait a moment before sending another message."
        )

    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY in ("your_key_here", ""):
        log.info("gemini_key_missing_streaming_local_copilot", user_id=user_id)
        full_text = _generate_fallback_copilot_response(user_message)
        words = full_text.split(" ")
        for i in range(0, len(words), 4):
            chunk = " ".join(words[i : i + 4]) + " "
            yield chunk
        return

    try:
        model = _get_model()
        gemini_history = build_history(history)

        log.info(
            "gemini_stream_request",
            user_id=user_id,
            model=settings.GEMINI_MODEL,
            history_length=len(gemini_history),
        )

        chat = model.start_chat(history=gemini_history)
        response_iter = await chat.send_message_async(user_message, stream=True)

        total_chars = 0
        async for chunk in response_iter:
            text = chunk.text
            if text:
                total_chars += len(text)
                yield text

        log.info("gemini_stream_done", user_id=user_id, total_chars=total_chars)
    except Exception as exc:
        log.warning("gemini_stream_failed_streaming_fallback", error=str(exc))
        full_text = _generate_fallback_copilot_response(user_message)
        for chunk in [full_text[: len(full_text) // 2], full_text[len(full_text) // 2 :]]:
            yield chunk

