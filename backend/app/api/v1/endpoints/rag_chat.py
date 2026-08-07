"""
RAG AI Infrastructure Chat Platform API Endpoints.
"""

import uuid

import structlog
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.crud.crud_rag_chat import crud_rag_chat
from app.schemas.rag_chat import (
    RAGHistoryResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGUploadResponse,
)
from app.services.rag_service import RAGService, rag_service
from app.services.vector_store_service import vector_store_service

log = structlog.get_logger(__name__)

router = APIRouter()


def get_rag_service() -> RAGService:
    return rag_service


@router.post(
    "/query",
    response_model=RAGQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Query RAG Infrastructure Chat",
)
async def query_rag_chat(
    req: RAGQueryRequest,
    db: AsyncSession = Depends(get_db),
    service: RAGService = Depends(get_rag_service),
):
    """Execute RAG question answering over ChromaDB vector telemetry collections using Google Gemini API."""
    return await service.answer_question(req)


@router.post(
    "/upload",
    response_model=RAGUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload telemetry document into vector store",
)
async def upload_telemetry_document(
    file: UploadFile = File(...),
    collection: str = Query(
        "logs",
        description="Vector collection: logs, incidents, metrics, alerts, traces, ai_reports",
    ),
    db: AsyncSession = Depends(get_db),
):
    """Upload custom log or telemetry file to index into ChromaDB vector store."""
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    doc_id = f"doc-up-{uuid.uuid4().hex[:8]}"

    vector_store_service.add_document(
        collection_name=collection,
        doc_id=doc_id,
        text=text,
        metadata={"filename": file.filename, "size_bytes": len(content)},
    )

    return RAGUploadResponse(
        filename=file.filename or "uploaded_log.txt",
        file_size_bytes=len(content),
        collection=collection,
        documents_indexed=1,
        status="success",
        message=f"File successfully indexed into '{collection}' vector collection.",
    )


@router.get("/history", response_model=RAGHistoryResponse, summary="Get conversation history")
async def get_chat_history(
    conversation_id: str = Query("conv-default", description="Conversation session ID"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve chat history messages for a session."""
    return await crud_rag_chat.get_history(db, conversation_id)


@router.delete("/history", summary="Clear conversation history")
async def clear_chat_history(
    conversation_id: str = Query("conv-default", description="Conversation session ID"),
    db: AsyncSession = Depends(get_db),
):
    """Clear conversation history for a session."""
    await crud_rag_chat.clear_history(db, conversation_id)
    return {"status": "success", "message": f"History for '{conversation_id}' cleared."}
