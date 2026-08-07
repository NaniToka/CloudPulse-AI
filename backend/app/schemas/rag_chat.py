"""
Pydantic v2 schemas for RAG AI Infrastructure Chat Platform.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    collection: str  # logs, incidents, metrics, alerts, traces, ai_reports
    title: str
    snippet: str
    relevance_score: float = 0.92
    metadata: dict[str, Any] = Field(default_factory=dict)


class RelatedItem(BaseModel):
    type: str  # alert, trace, incident
    id: str
    title: str
    status: str = "open"
    severity: str | None = None


class RAGQueryRequest(BaseModel):
    question: str = Field(
        ..., min_length=2, max_length=2000, description="User question about infrastructure"
    )
    collection_filter: list[str] | None = Field(
        default=None, description="Optional vector collections filter"
    )
    conversation_id: str | None = Field(None, description="Optional conversation session ID")


class RAGQueryResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"msg-{uuid.uuid4().hex[:12]}")
    conversation_id: str
    question: str
    answer: str
    evidence_sources: list[SourceCitation] = Field(default_factory=list)
    confidence_score: float = Field(default=0.94, ge=0.0, le=1.0)
    related_alerts: list[RelatedItem] = Field(default_factory=list)
    related_traces: list[RelatedItem] = Field(default_factory=list)
    related_incidents: list[RelatedItem] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    suggested_followup_questions: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RAGUploadResponse(BaseModel):
    filename: str
    file_size_bytes: int
    collection: str
    documents_indexed: int
    status: str = "success"
    message: str


class RAGHistoryItem(BaseModel):
    id: str
    question: str
    answer: str
    confidence_score: float
    created_at: datetime


class RAGHistoryResponse(BaseModel):
    conversation_id: str
    messages: list[RAGHistoryItem]
    total_messages: int
