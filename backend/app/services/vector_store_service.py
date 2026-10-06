"""
ChromaDB Vector Store Service — Manages 6 ChromaDB collections:
logs, incidents, metrics, alerts, traces, ai_reports.
"""

import os
from typing import Any

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
        self.collections: dict[str, Any] = {}
        self.in_memory_docs: dict[str, list[dict[str, Any]]] = {c: [] for c in COLLECTION_NAMES}
        self._initialize_chromadb()

    def _initialize_chromadb(self) -> None:
        """Initialize ChromaDB client and create 6 collections.

        ChromaDB is an optional dependency. When not installed the service
        runs entirely in-memory (keyword search fallback). This keeps the
        free-tier Docker container under 512 MB RAM.

        To enable persistent storage: install chromadb==0.5.5 and set
        CHROMA_DATA_DIR to a writable path (e.g. a mounted volume).
        We pass embedding_function=None so ChromaDB never downloads the
        79 MB all-MiniLM-L6-v2 ONNX model.
        """
        try:
            import tempfile

            import chromadb  # optional — not in requirements for free-tier deploy
            from chromadb.config import Settings
            persist_dir = os.environ.get(
                "CHROMA_DATA_DIR",
                os.path.join(tempfile.gettempdir(), "chroma_db_data"),
            )
            os.makedirs(persist_dir, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(anonymized_telemetry=False),
            )

            for col in COLLECTION_NAMES:
                # embedding_function=None: we manage embeddings ourselves.
                # This prevents ChromaDB from auto-downloading ONNX models.
                collection_obj = self.chroma_client.get_or_create_collection(
                    name=col,
                    metadata={"hnsw:space": "cosine"},
                    embedding_function=None,  # type: ignore[arg-type]
                )
                self.collections[col] = collection_obj
            log.info("chromadb_vector_store_initialized", collections=COLLECTION_NAMES)
        except ImportError:
            log.info("chromadb_not_installed_using_in_memory_fallback")
        except Exception as exc:
            log.warning("chromadb_init_fallback_in_memory", error=str(exc))

    def add_document(
        self, collection_name: str, doc_id: str, text: str, metadata: dict[str, Any]
    ) -> None:
        """Adds a document to a specific vector collection."""
        if collection_name not in COLLECTION_NAMES:
            collection_name = "logs"

        doc_item = {
            "id": doc_id,
            "text": text,
            "metadata": metadata,
            "collection": collection_name,
        }

        # Persist to ChromaDB using a placeholder embedding (all zeros).
        # We do NOT use ChromaDB's built-in embedding function to avoid
        # downloading the 79 MB ONNX model. Similarity search is handled
        # by the keyword fallback below; ChromaDB is used for persistence only.
        if collection_name in self.collections:
            try:
                # Store text in metadata so we can retrieve it on restart
                meta_with_text = {**metadata, "_text": text[:2000]}
                self.collections[collection_name].upsert(
                    ids=[doc_id],
                    embeddings=[[0.0] * 384],  # placeholder — not used for search
                    metadatas=[meta_with_text],
                )
            except Exception as exc:
                log.error("chromadb_upsert_failed", collection=collection_name, error=str(exc))

        # Store in fallback in-memory cache (deduplicated by id)
        existing = [d for d in self.in_memory_docs[collection_name] if d["id"] != doc_id]
        existing.append(doc_item)
        self.in_memory_docs[collection_name] = existing

    def query_similarity(
        self,
        query: str,
        collection_filter: list[str] | None = None,
        top_k: int = 4,
    ) -> list[dict[str, Any]]:
        """Queries collections for relevant context documents via keyword matching.

        ChromaDB is used as a persistence backend only; all similarity search
        is done in-memory via keyword overlap to avoid triggering the ONNX
        embedding model download.
        """
        target_collections = collection_filter or COLLECTION_NAMES
        results = []
        seen_ids = set()

        query_terms = [t.lower() for t in query.split() if len(t) > 2]

        for col_name in target_collections:
            if col_name not in COLLECTION_NAMES:
                continue

            # Rebuild in-memory index from ChromaDB if empty (e.g. after restart)
            if col_name in self.collections and not self.in_memory_docs.get(col_name):
                try:
                    count = self.collections[col_name].count()
                    if count > 0:
                        # Fetch all stored docs via metadata (no query_texts needed)
                        res = self.collections[col_name].get(
                            include=["metadatas", "ids"],
                            limit=200,
                        )
                        ids = res.get("ids", [])
                        metas = res.get("metadatas", [])
                        for i, doc_id in enumerate(ids):
                            meta = metas[i] if i < len(metas) else {}
                            text = meta.pop("_text", "")
                            if text and doc_id not in {d["id"] for d in self.in_memory_docs[col_name]}:
                                self.in_memory_docs[col_name].append({
                                    "id": doc_id,
                                    "text": text,
                                    "metadata": meta,
                                    "collection": col_name,
                                })
                except Exception as exc:
                    log.debug("chromadb_restore_failed", collection=col_name, error=str(exc))

            # Keyword search across in-memory docs
            for doc in self.in_memory_docs.get(col_name, []):
                if doc["id"] in seen_ids:
                    continue
                doc_text_lower = doc["text"].lower()
                matches = sum(1 for term in query_terms if term in doc_text_lower)
                if matches > 0:
                    seen_ids.add(doc["id"])
                    results.append(
                        {
                            "collection": col_name,
                            "id": doc["id"],
                            "text": doc["text"],
                            "metadata": doc["metadata"],
                            "score": round(0.7 + min(0.28, matches * 0.08), 2),
                        }
                    )

        # Sort by relevance score desc
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]



vector_store_service = VectorStoreService()
