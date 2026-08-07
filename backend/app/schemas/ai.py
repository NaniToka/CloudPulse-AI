"""
Pydantic schemas for the AI Copilot module.

ChatRequest   — user message + optional conversation context
ChatResponse  — full assistant reply (non-streaming)
MessageSchema — a single message as stored in the DB / returned in history
SessionSchema — a chat session with its messages
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator

# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------


class MessageSchema(BaseModel):
    """A single chat message — mirrors the ChatMessage ORM model."""

    id: uuid.UUID
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionSchema(BaseModel):
    """A chat session with nested messages."""

    id: uuid.UUID
    title: str | None
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    messages: list[MessageSchema] = []

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# POST /ai/chat  request / response
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    """
    Body sent by the frontend for each chat turn.

    Fields
    ------
    message       : The user's latest message text.
    session_id    : If provided, messages are appended to that session.
                    If None, a new session is created automatically.
    stream        : Whether to use Server-Sent Events streaming.
                    Frontend should set to True for the typing animation effect.
    """

    message: str
    session_id: uuid.UUID | None = None
    stream: bool = False

    @field_validator("message")
    @classmethod
    def _message_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty.")
        if len(v) > 8_000:
            raise ValueError("Message exceeds 8,000 character limit.")
        return v


class ChatResponse(BaseModel):
    """Response body for non-streaming POST /ai/chat."""

    session_id: uuid.UUID
    message_id: uuid.UUID  # ID of the assistant ChatMessage row
    reply: str
    model: str


# ---------------------------------------------------------------------------
# GET /ai/history  response
# ---------------------------------------------------------------------------


class HistoryResponse(BaseModel):
    sessions: list[SessionSchema]
    total: int
