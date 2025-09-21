"""Hybrid retriever combining dense and sparse search with reranking."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, List, Sequence
import logging

try:  # pragma: no cover - optional heavy deps
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore

try:  # pragma: no cover
    from rank_bm25 import BM25Okapi
except Exception:  # pragma: no cover
    BM25Okapi = None  # type: ignore

try:  # pragma: no cover
    from FlagEmbedding import FlagReranker
except Exception:  # pragma: no cover
    FlagReranker = None  # type: ignore

from .vector_store import QdrantVectorStore

LOGGER = logging.getLogger(__name__)


@dataclass
class EmbeddingService:
    """Wrapper around BAAI embedding models."""

    model_name: str = "BAAI/bge-large-zh"
    device: str | None = None
    _model: SentenceTransformer | None = field(default=None, init=False, repr=False)

    def _ensure_model(self) -> SentenceTransformer:
        if SentenceTransformer is None:  # pragma: no cover - import guard
            raise ImportError("sentence-transformers is required for EmbeddingService")
        if self._model is None:
            LOGGER.info("Loading embedding model: %s", self.model_name)
            self._model = SentenceTransformer(self.model_name, device=self.device)
        return self._model

    def encode(self, texts: Sequence[str]) -> List[List[float]]:
        model = self._ensure_model()
        return model.encode(list(texts), convert_to_numpy=True).tolist()


@dataclass
class RerankerService:
    """Wrap the BAAI reranker model."""

    model_name: str = "BAAI/bge-reranker-large"
    device: str | None = None
    _model: FlagReranker | None = field(default=None, init=False, repr=False)

    def _ensure_model(self) -> FlagReranker:
        if FlagReranker is None:  # pragma: no cover
            raise ImportError("FlagEmbedding is required for RerankerService")
        if self._model is None:
            LOGGER.info("Loading reranker model: %s", self.model_name)
            self._model = FlagReranker(self.model_name, use_fp16=self.device == "cuda")
        return self._model

    def rerank(self, query: str, documents: Sequence[str], top_k: int = 5) -> List[int]:
        model = self._ensure_model()
        scores = model.compute_score([[query, doc] for doc in documents])
        ranked_indices = sorted(range(len(documents)), key=lambda i: scores[i], reverse=True)
        return ranked_indices[:top_k]


@dataclass
class HybridRetriever:
    """Combine dense embedding similarity with BM25 sparse search."""

    vector_store: QdrantVectorStore
    embedding_service: EmbeddingService
    reranker: RerankerService | None = None
    bm25_tokenizer: Callable[[str], Sequence[str]] | None = None
    _bm25: BM25Okapi | None = field(default=None, init=False, repr=False)
    _documents: List[str] = field(default_factory=list, init=False, repr=False)

    def index(self, documents: Iterable[dict]) -> None:
        """Index documents in the vector store and prepare BM25 corpus."""

        texts = []
        payloads = []
        for doc in documents:
            text = doc.get("text")
            if not text:
                continue
            texts.append(text)
            payloads.append(doc)
        if not texts:
            return
        embeddings = self.embedding_service.encode(texts)
        self.vector_store.ensure_collection(vector_size=len(embeddings[0]))
        self.vector_store.upsert(embeddings, payloads)

        tokenizer = self.bm25_tokenizer or (lambda x: x.split())
        tokenized = [tokenizer(text) for text in texts]
        if BM25Okapi is None:  # pragma: no cover
            LOGGER.warning("rank_bm25 is not installed; BM25 retrieval disabled")
        else:
            self._bm25 = BM25Okapi(tokenized)
            self._documents = texts

    def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        """Retrieve documents using a hybrid search strategy."""

        dense_embedding = self.embedding_service.encode([query])[0]
        dense_results = self.vector_store.search(dense_embedding, limit=top_k * 2)

        sparse_results: List[dict] = []
        if self._bm25 is not None:
            scores = self._bm25.get_scores((self.bm25_tokenizer or (lambda x: x.split()))(query))
            ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[: top_k * 2]
            sparse_results = [
                {"text": self._documents[idx], "source": "bm25", "score": float(scores[idx])}
                for idx in ranked
            ]

        combined = dense_results + sparse_results
        if not combined:
            return []

        if self.reranker is not None:
            rerank_indices = self.reranker.rerank(query, [doc["text"] for doc in combined], top_k=top_k)
            return [combined[idx] for idx in rerank_indices]
        return combined[:top_k]


__all__ = ["HybridRetriever", "EmbeddingService", "RerankerService"]
