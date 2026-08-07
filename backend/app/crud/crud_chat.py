"""
CRUD helpers for ChatSession and ChatMessage.

Design
------
- Sessions are scoped to a user — every query filters by user_id.
- Messages are always loaded via their parent session; we never load
  them globally without a session constraint.
- All DB access is async (AsyncSession).
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession

# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------


async def get_session(
    db: AsyncSession,
    *,
    session_id: uuid.UUID,
    user_id: uuid.UUID,
) -> ChatSession | None:
    """Return a session owned by user_id, with messages pre-loaded."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .options(selectinload(ChatSession.messages))
    )
    return result.scalar_one_or_none()


async def create_session(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    title: str | None = None,
) -> ChatSession:
    """Create a new chat session for the given user."""
    session = ChatSession(user_id=user_id, title=title)
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return session


async def list_sessions(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    limit: int = 50,
) -> list[ChatSession]:
    """Return the most recent sessions for user_id, newest first."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .options(selectinload(ChatSession.messages))
        .order_by(ChatSession.updated_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def delete_all_sessions(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
) -> int:
    """
    Delete all sessions (and their messages via cascade) for user_id.
    Returns the number of sessions deleted.
    """
    result = await db.execute(select(ChatSession).where(ChatSession.user_id == user_id))
    sessions = list(result.scalars().all())
    for s in sessions:
        await db.delete(s)
    await db.flush()
    return len(sessions)


async def update_session_title(
    db: AsyncSession,
    *,
    session: ChatSession,
    title: str,
) -> ChatSession:
    """Set a human-readable title on a session (derived from the first message)."""
    session.title = title
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return session


# ---------------------------------------------------------------------------
# Message helpers
# ---------------------------------------------------------------------------


async def add_message(
    db: AsyncSession,
    *,
    session_id: uuid.UUID,
    role: str,
    content: str,
) -> ChatMessage:
    """Append a message to a session and return the new ChatMessage row."""
    msg = ChatMessage(session_id=session_id, role=role, content=content)
    db.add(msg)
    await db.flush()
    await db.refresh(msg)
    return msg


async def get_recent_messages(
    db: AsyncSession,
    *,
    session_id: uuid.UUID,
    limit: int = 20,
) -> list[ChatMessage]:
    """
    Return the last *limit* messages for a session, oldest-first.

    We cap at 20 to keep the Gemini context window manageable.  The
    ``build_history`` helper in ai_service.py converts these to the
    Gemini format.
    """
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    return list(result.scalars().all())
