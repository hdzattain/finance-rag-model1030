"""Qdrant vector store wrapper used by the RAG subsystem."""
from __future__ import annotations

import logging
from typing import List, Sequence

try:  # pragma: no cover - optional dependency
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except Exception:  # pragma: no cover - fallback
    QdrantClient = None  # type: ignore
    Distance = VectorParams = PointStruct = object  # type: ignore

LOGGER = logging.getLogger(__name__)


class QdrantVectorStore:
    """Utility class encapsulating qdrant operations."""

    def __init__(self, host: str, port: int, collection_name: str, api_key: str | None = None) -> None:
        if QdrantClient is None:
            raise ImportError("qdrant-client is required for QdrantVectorStore")
        self.collection_name = collection_name
        self.client = QdrantClient(host=host, port=port, api_key=api_key)

    def ensure_collection(self, vector_size: int) -> None:
        """Create the collection if it does not exist."""

        try:
            self.client.get_collection(self.collection_name)
        except Exception:  # pragma: no cover - remote call
            LOGGER.info("Creating Qdrant collection: %s", self.collection_name)
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def upsert(self, embeddings: Sequence[Sequence[float]], payloads: Sequence[dict]) -> None:
        """Insert vectors into the collection."""

        points = [
            PointStruct(id=idx, vector=vector, payload=payload)
            for idx, (vector, payload) in enumerate(zip(embeddings, payloads))
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, embedding: Sequence[float], limit: int = 5) -> List[dict]:
        """Search for similar vectors and return payloads."""

        result = self.client.search(collection_name=self.collection_name, query_vector=embedding, limit=limit)
        return [hit.payload for hit in result]


__all__ = ["QdrantVectorStore"]
