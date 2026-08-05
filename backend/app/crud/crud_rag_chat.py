"""
CRUD Repository for RAG Chat History & Messages.
"""

import uuid
from typing import List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.rag_chat import RAGHistoryItem, RAGHistoryResponse

# In-memory session message store for RAG conversations
_rag_history_store: Dict[str, List[Dict[str, Any]]] = {}


class CRUDRAGChat:
    """Repository for storing and retrieving RAG Chat history sessions."""

    async def add_message(self, conversation_id: str, question: str, answer: str, confidence_score: float = 0.95) -> None:
        """Stores a Q&A exchange in history."""
        if conversation_id not in _rag_history_store:
            _rag_history_store[conversation_id] = []

        _rag_history_store[conversation_id].append({
            "id": f"msg-{uuid.uuid4().hex[:12]}",
            "question": question,
            "answer": answer,
            "confidence_score": confidence_score,
            "created_at": datetime.now(timezone.utc),
        })

    async def get_history(self, db: AsyncSession, conversation_id: str) -> RAGHistoryResponse:
        """Fetch chat history messages for a conversation ID."""
        raw_items = _rag_history_store.get(conversation_id, [])

        items = []
        for msg in raw_items:
            items.append(
                RAGHistoryItem(
                    id=msg["id"],
                    question=msg["question"],
                    answer=msg["answer"],
                    confidence_score=msg["confidence_score"],
                    created_at=msg["created_at"],
                )
            )

        return RAGHistoryResponse(
            conversation_id=conversation_id,
            messages=items,
            total_messages=len(items),
        )

    async def clear_history(self, db: AsyncSession, conversation_id: str) -> bool:
        """Clear chat history for a session."""
        if conversation_id in _rag_history_store:
            _rag_history_store[conversation_id] = []
        return True


crud_rag_chat = CRUDRAGChat()
