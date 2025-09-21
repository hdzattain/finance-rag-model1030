"""Research orchestration combining automated and human-in-the-loop analysis."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Protocol


class ResearchTool(Protocol):
    """Protocol for research tooling (e.g. paper search APIs)."""

    def search(self, query: str) -> List[dict]:
        ...


@dataclass
class DummyPaperSearchTool:
    """Placeholder tool returning canned results."""

    def search(self, query: str) -> List[dict]:  # type: ignore[override]
        return [
            {"title": "Chan Theory in Quantitative Trading", "summary": "讨论缠论与量化策略结合的研究。"},
            {"title": "Agentic RAG for Finance", "summary": "介绍金融场景的检索增强生成系统。"},
        ]


@dataclass
class ResearchCoordinator:
    """Coordinate automated research tasks and capture human notes."""

    tools: Iterable[ResearchTool] = field(default_factory=lambda: [DummyPaperSearchTool()])
    human_notes: List[str] = field(default_factory=list)

    def run_auto_research(self, query: str) -> List[dict]:
        results: List[dict] = []
        for tool in self.tools:
            results.extend(tool.search(query))
        return results

    def add_human_insight(self, note: str) -> None:
        self.human_notes.append(note)

    def compile_report(self, query: str) -> dict:
        return {
            "query": query,
            "auto_research": self.run_auto_research(query),
            "human_notes": list(self.human_notes),
        }


__all__ = ["ResearchCoordinator", "DummyPaperSearchTool"]
