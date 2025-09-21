"""Agentic RAG pipeline with iterative summarisation and research."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List
import logging

from ..config import PlatformConfig
from ..llm import BaseLLMClient
from .retriever import EmbeddingService, HybridRetriever, RerankerService
from .vector_store import QdrantVectorStore

LOGGER = logging.getLogger(__name__)


@dataclass
class _InMemoryRetriever:
    """Fallback retriever used when external dependencies are unavailable."""

    documents: List[dict] = field(default_factory=list)

    def index(self, documents: Iterable[dict]) -> None:
        for doc in documents:
            if doc.get("text"):
                self.documents.append(doc)

    def retrieve(self, query: str, top_k: int = 5) -> List[dict]:  # noqa: D401 - simple wrapper
        return self.documents[:top_k]


class AgenticRAGPipeline:
    """High level agent orchestrating retrieval and synthesis."""

    config: PlatformConfig
    llm_client: BaseLLMClient
    retriever: HybridRetriever | _InMemoryRetriever | None = None
    _conversation_summary: List[str] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.retriever is None:
            try:
                embedding_service = EmbeddingService()
                reranker = RerankerService()
                vector_store = QdrantVectorStore(
                    host=self.config.qdrant.host,
                    port=self.config.qdrant.port,
                    api_key=self.config.qdrant.api_key,
                    collection_name=self.config.qdrant.collection_name,
                )
                self.retriever = HybridRetriever(
                    vector_store=vector_store, embedding_service=embedding_service, reranker=reranker
                )
            except Exception as exc:  # pragma: no cover - dependency missing path
                LOGGER.warning("Falling back to in-memory retriever: %s", exc)
                self.retriever = _InMemoryRetriever()

    def ingest(self, documents: Iterable[dict]) -> None:
        """Index new documents into the hybrid retriever."""

        if self.retriever is None:
            self.retriever = _InMemoryRetriever()
        try:
            self.retriever.index(documents)
        except Exception as exc:  # pragma: no cover - dependency missing path
            LOGGER.warning("Hybrid retriever ingest failed, switching to in-memory store: %s", exc)
            fallback = _InMemoryRetriever()
            fallback.index(documents)
            self.retriever = fallback

    def _iterate_summary(self, query: str, retrieved: List[dict]) -> str:
        """Iteratively summarise retrieved content guided by the LLM agent."""

        summary_prompt = """
你是一名量化投研助手，需要结合缠论与量化策略思想对下面材料进行总结。
重点提取：
1. 核心观点和市场结构（缠论中趋势、盘整、买卖点）。
2. 对量化策略可操作的指标或因子。
3. 潜在的风险提示与回测假设。
输出以要点形式列出。
材料：{context}
问题：{query}
"""
        context = "\n\n".join(doc.get("text", "") for doc in retrieved)
        prompt = summary_prompt.format(context=context, query=query)
        summary = self.llm_client.generate(prompt)
        self._conversation_summary.append(summary)
        return summary

    def _research_iteration(self, query: str, iteration: int) -> str:
        """Ask the agent to propose further research directions."""

        exploration_prompt = f"""
基于已有摘要：{self._conversation_summary[-1] if self._conversation_summary else '无'}
第 {iteration} 轮研究，请列出需要补充的数据点、可能的回测参数和与缠论结构相关的验证步骤。
"""
        return self.llm_client.generate(exploration_prompt)

    def run(self, query: str, rounds: int = 2, top_k: int = 5) -> dict:
        """Execute the agentic RAG loop."""

        if self.retriever is None:
            return {"answer": "未检索到有效信息", "research": []}
        try:
            retrieved = self.retriever.retrieve(query, top_k=top_k)
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Retrieval failed, returning empty result: %s", exc)
            retrieved = []
        if not retrieved:
            return {"answer": "未检索到有效信息", "research": []}
        summary = self._iterate_summary(query, retrieved)
        research_plan = []
        for idx in range(rounds):
            research_plan.append(self._research_iteration(query, idx + 1))
        answer_prompt = f"""
请基于总结与研究计划，给出针对问题《{query}》的量化建议，
包括：
- 缠论结构判断与趋势级别
- 推荐的量化因子与参数
- 需要补充的外部数据
- 建议的风险控制与回测平台
"""
        answer = self.llm_client.generate(answer_prompt)
        return {"answer": answer, "summary": summary, "research": research_plan, "sources": retrieved}


__all__ = ["AgenticRAGPipeline"]
