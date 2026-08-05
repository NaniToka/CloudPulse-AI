"""
ChromaDB Vector Store Service — Manages 6 ChromaDB collections:
logs, incidents, metrics, alerts, traces, ai_reports.
"""

import os
import uuid
from typing import Any, Dict, List, Optional
import structlog

log = structlog.get_logger(__name__)

COLLECTION_NAMES = [
    "logs",
    "incidents",
    "metrics",
    "alerts",
    "traces",
    "ai_reports",
]


class VectorStoreService:
    """ChromaDB Vector Store Service with collection retrieval & semantic search."""

    def __init__(self) -> None:
        self.chroma_client = None
        self.collections: Dict[str, Any] = {}
        self.in_memory_docs: Dict[str, List[Dict[str, Any]]] = {c: [] for c in COLLECTION_NAMES}
        self._initialize_chromadb()

    def _initialize_chromadb(self) -> None:
        """Initialize ChromaDB client and create 6 collections."""
        try:
            import chromadb

            persist_dir = os.path.join(os.getcwd(), "chroma_db_data")
            os.makedirs(persist_dir, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(path=persist_dir)

            for col in COLLECTION_NAMES:
                collection_obj = self.chroma_client.get_or_create_collection(
                    name=col,
                    metadata={"hnsw:space": "cosine"},
                )
                self.collections[col] = collection_obj
            log.info("chromadb_vector_store_initialized", collections=COLLECTION_NAMES)
        except Exception as exc:
            log.warning("chromadb_init_fallback_in_memory", error=str(exc))

    def add_document(self, collection_name: str, doc_id: str, text: str, metadata: Dict[str, Any]) -> None:
        """Adds a document to a specific vector collection."""
        if collection_name not in COLLECTION_NAMES:
            collection_name = "logs"

        doc_item = {
            "id": doc_id,
            "text": text,
            "metadata": metadata,
            "collection": collection_name,
        }

        # Store in ChromaDB if available
        if collection_name in self.collections:
            try:
                self.collections[collection_name].upsert(
                    ids=[doc_id],
                    documents=[text],
                    metadatas=[metadata],
                )
            except Exception as exc:
                log.error("chromadb_upsert_failed", collection=collection_name, error=str(exc))

        # Store in fallback in-memory cache
        self.in_memory_docs[collection_name].append(doc_item)

    def query_similarity(
        self,
        query: str,
        collection_filter: Optional[List[str]] = None,
        top_k: int = 4,
    ) -> List[Dict[str, Any]]:
        """Queries across ChromaDB collections for relevant context documents."""
        target_collections = collection_filter or COLLECTION_NAMES
        results = []

        query_terms = [t.lower() for t in query.split() if len(t) > 2]

        for col_name in target_collections:
            if col_name not in COLLECTION_NAMES:
                continue

            # Query ChromaDB collection if active
            if col_name in self.collections:
                try:
                    res = self.collections[col_name].query(
                        query_texts=[query],
                        n_results=min(top_k, 5),
                    )
                    if res and res.get("documents") and len(res["documents"]) > 0:
                        docs = res["documents"][0]
                        metas = res.get("metadatas", [[]])[0]
                        ids = res.get("ids", [[]])[0]
                        for idx, d_text in enumerate(docs):
                            results.append({
                                "collection": col_name,
                                "id": ids[idx] if idx < len(ids) else f"{col_name}-{idx}",
                                "text": d_text,
                                "metadata": metas[idx] if idx < len(metas) else {},
                                "score": 0.95,
                            })
                except Exception as exc:
                    log.debug("chromadb_query_failed", collection=col_name, error=str(exc))

            # Query in-memory docs fallback
            for doc in self.in_memory_docs.get(col_name, []):
                doc_text_lower = doc["text"].lower()
                matches = sum(1 for term in query_terms if term in doc_text_lower)
                if matches > 0:
                    results.append({
                        "collection": col_name,
                        "id": doc["id"],
                        "text": doc["text"],
                        "metadata": doc["metadata"],
                        "score": round(0.7 + min(0.28, matches * 0.08), 2),
                    })

        # Sort by relevance score desc
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


vector_store_service = VectorStoreService()
