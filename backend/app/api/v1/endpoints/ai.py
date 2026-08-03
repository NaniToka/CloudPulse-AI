"""
AI Copilot endpoints.

Routes
------
POST   /api/v1/ai/chat     — send a message, get a reply (stream or full)
GET    /api/v1/ai/history  — list this user's chat sessions
DELETE /api/v1/ai/history  — delete all chat history for this user

Authentication
--------------
All routes require a valid JWT Bearer token (require_active_user dependency).

Streaming
---------
When ChatRequest.stream == True the endpoint returns a StreamingResponse
whose body is a sequence of Server-Sent Events (SSE):

    data: <text chunk>\n\n
    ...
    data: [DONE]\n\n

The frontend reads these with the native EventSource API or with a
ReadableStream + TextDecoder (used in our implementation).

Error handling
--------------
- Missing Gemini API key  → HTTP 503 with actionable message
- Rate limit exceeded     → HTTP 429
- Any Gemini SDK error    → HTTP 502 with sanitised message
- Validation errors       → HTTP 422 (handled globally)
"""

from __future__ import annotations

import json
import uuid
from typing import AsyncGenerator

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_active_user
from app.core.config import settings
from app.crud import crud_chat
from app.models.user import User
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
    SessionSchema,
)
from app.services.ai_service import (
    build_history,
    chat_completion,
    stream_chat_completion,
)

log = structlog.get_logger(__name__)
router = APIRouter()

# Maximum messages kept per session to avoid unbounded DB growth
_MAX_HISTORY_MESSAGES = 40


# ---------------------------------------------------------------------------
# POST /ai/chat
# ---------------------------------------------------------------------------

@router.post(
    "/chat",
    summary="Send a message to the AI Copilot",
    response_model=None,   # varies: ChatResponse or StreamingResponse
)
async def chat(
    payload: ChatRequest,
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send *payload.message* to Gemini and return (or stream) the reply.

    Session management
    ------------------
    If *payload.session_id* is given the message is appended to that session.
    Otherwise a new session is created automatically.  The session ID is
    always returned in the response so the frontend can track it.

    The most recent 20 messages from the session are passed as conversation
    history to Gemini on every turn.
    """
    user_id = current_user.id
    log.info("ai_chat_request", user_id=str(user_id), stream=payload.stream)

    # ── 1. Resolve or create session ──────────────────────────────────────
    if payload.session_id:
        session = await crud_chat.get_session(
            db, session_id=payload.session_id, user_id=user_id
        )
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found or does not belong to you.",
            )
    else:
        # Auto-title from the first ~60 chars of the user message
        auto_title = payload.message[:60].strip()
        if len(payload.message) > 60:
            auto_title += "…"
        session = await crud_chat.create_session(db, user_id=user_id, title=auto_title)

    session_id: uuid.UUID = session.id

    # ── 2. Persist user message ────────────────────────────────────────────
    await crud_chat.add_message(
        db, session_id=session_id, role="user", content=payload.message
    )

    # ── 3. Build Gemini history (last N messages, excluding the one we just added) ──
    recent = await crud_chat.get_recent_messages(
        db, session_id=session_id, limit=_MAX_HISTORY_MESSAGES
    )
    # Exclude the message we just inserted (last item) from history fed to AI
    history_dicts = [
        {"role": m.role, "content": m.content}
        for m in recent[:-1]  # all but the latest user message
    ]

    # ── 4a. Streaming path ─────────────────────────────────────────────────
    if payload.stream:
        return StreamingResponse(
            _sse_generator(
                user_message=payload.message,
                history=history_dicts,
                user_id=str(user_id),
                session_id=session_id,
                db=db,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "X-Session-Id": str(session_id),   # frontend reads this to track the session
            },
        )

    # ── 4b. Non-streaming path ─────────────────────────────────────────────
    try:
        reply = await chat_completion(
            user_message=payload.message,
            history=history_dicts,
            user_id=str(user_id),
        )
    except ValueError as exc:
        # Rate limit
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))
    except RuntimeError as exc:
        # Missing API key
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except Exception as exc:
        log.error("gemini_error", error=str(exc), user_id=str(user_id))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI service returned an error. Please try again.",
        )

    # ── 5. Persist assistant reply ─────────────────────────────────────────
    ai_msg = await crud_chat.add_message(
        db, session_id=session_id, role="assistant", content=reply
    )

    log.info("ai_chat_success", user_id=str(user_id), session_id=str(session_id))

    return ChatResponse(
        session_id=session_id,
        message_id=ai_msg.id,
        reply=reply,
        model=settings.GEMINI_MODEL,
    )


async def _sse_generator(
    user_message: str,
    history: list[dict],
    user_id: str,
    session_id: uuid.UUID,
    db: AsyncSession,
) -> AsyncGenerator[str, None]:
    """
    Yield Server-Sent Event frames containing Gemini stream chunks.

    Protocol:
        data: <chunk text>\\n\\n        — partial content
        data: [DONE]\\n\\n             — stream finished successfully
        data: [ERROR] <msg>\\n\\n      — stream finished with an error

    The complete assembled text is persisted to the DB after streaming ends.
    """
    full_reply: list[str] = []

    try:
        async for chunk in stream_chat_completion(
            user_message=user_message,
            history=history,
            user_id=user_id,
        ):
            full_reply.append(chunk)
            # Escape any literal newlines inside the chunk so SSE framing
            # isn't broken — the client re-assembles them.
            safe = chunk.replace("\n", "\\n")
            yield f"data: {safe}\n\n"

        # Persist the complete reply
        await crud_chat.add_message(
            db,
            session_id=session_id,
            role="assistant",
            content="".join(full_reply),
        )
        yield "data: [DONE]\n\n"

    except ValueError as exc:
        yield f"data: [ERROR] {exc}\n\n"
    except RuntimeError as exc:
        yield f"data: [ERROR] {exc}\n\n"
    except Exception as exc:
        log.error("gemini_stream_error", error=str(exc))
        yield "data: [ERROR] The AI service returned an error. Please try again.\n\n"


# ---------------------------------------------------------------------------
# GET /ai/history
# ---------------------------------------------------------------------------

@router.get(
    "/history",
    response_model=HistoryResponse,
    summary="Retrieve this user's chat history",
)
async def get_history(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
) -> HistoryResponse:
    sessions = await crud_chat.list_sessions(db, user_id=current_user.id, limit=50)
    return HistoryResponse(
        sessions=[SessionSchema.model_validate(s) for s in sessions],
        total=len(sessions),
    )


# ---------------------------------------------------------------------------
# DELETE /ai/history
# ---------------------------------------------------------------------------

@router.delete(
    "/history",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all chat history for this user",
    response_class=StreamingResponse,  # satisfy FastAPI 0.111 204 constraint
)
async def delete_history(
    current_user: User = Depends(require_active_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await crud_chat.delete_all_sessions(db, user_id=current_user.id)
    log.info("ai_history_deleted", user_id=str(current_user.id), sessions_deleted=deleted)
