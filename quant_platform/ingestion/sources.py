"""Data acquisition layer for integrating new knowledge into the RAG store."""
from __future__ import annotations

import asyncio
import datetime as dt
import logging
from dataclasses import dataclass, field
from typing import Iterable, List, Protocol

import json

import requests

from ..config import DataSourceConfig

LOGGER = logging.getLogger(__name__)


class DocumentSink(Protocol):
    """Protocol representing objects capable of ingesting documents."""

    def ingest(self, documents: Iterable[dict]) -> None:
        ...


@dataclass
class SnowballSource:
    """Retrieve latest posts from Snowball (雪球)."""

    cookie: str | None

    def fetch(self, symbol: str, limit: int = 20) -> List[dict]:
        if not self.cookie:
            LOGGER.warning("Snowball cookie missing; skipping fetch")
            return []
        url = "https://stock.xueqiu.com/v5/stock/chart/kline.json"
        params = {"symbol": symbol, "begin": int(dt.datetime.utcnow().timestamp() * 1000), "period": "day"}
        headers = {"Cookie": self.cookie, "User-Agent": "Mozilla/5.0"}
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:
            LOGGER.warning("Snowball fetch failed: %s", exc)
            return []
        data = resp.json().get("data", {})
        items = data.get("items", [])[-limit:]
        return [
            {
                "source": "snowball",
                "symbol": symbol,
                "timestamp": item[0],
                "text": json.dumps(item, ensure_ascii=False),
            }
            for item in items
        ]


@dataclass
class AShareIndexSource:
    """Fetch A-share index snapshots."""

    def fetch(self, symbols: Iterable[str]) -> List[dict]:
        documents: List[dict] = []
        for symbol in symbols:
            doc = {
                "source": "a-share-index",
                "symbol": symbol,
                "timestamp": int(dt.datetime.utcnow().timestamp()),
                "text": f"指数 {symbol} 最新快照时间 {dt.datetime.utcnow().isoformat()}"
            }
            documents.append(doc)
        return documents


@dataclass
class ResearchReportSource:
    """Generic financial institution research report fetcher (placeholder)."""

    api_token: str | None

    def fetch(self, topic: str) -> List[dict]:
        if not self.api_token:
            LOGGER.warning("Research report API token missing")
            return []
        # Placeholder: in practice query vendor API
        return [
            {
                "source": "research-report",
                "topic": topic,
                "timestamp": int(dt.datetime.utcnow().timestamp()),
                "text": f"研究主题 {topic} 的最新研报摘要。",
            }
        ]


@dataclass
class DataIngestionManager:
    """Coordinate ingestion tasks and push data into RAG."""

    config: DataSourceConfig
    sink: DocumentSink

    def ingest_all(self, snowball_symbols: Iterable[str], index_symbols: Iterable[str], topics: Iterable[str]) -> None:
        snowball = SnowballSource(cookie=self.config.snowball_cookie)
        index_source = AShareIndexSource()
        research_source = ResearchReportSource(api_token=self.config.research_api_token)

        documents = []
        for symbol in snowball_symbols:
            documents.extend(snowball.fetch(symbol))
        documents.extend(index_source.fetch(index_symbols))
        for topic in topics:
            documents.extend(research_source.fetch(topic))

        if documents:
            LOGGER.info("Ingested %d documents", len(documents))
            self.sink.ingest(documents)

    async def ingest_periodically(
        self,
        snowball_symbols: Iterable[str],
        index_symbols: Iterable[str],
        topics: Iterable[str],
        interval_minutes: int = 30,
    ) -> None:
        while True:
            self.ingest_all(snowball_symbols, index_symbols, topics)
            await asyncio.sleep(interval_minutes * 60)


__all__ = ["DataIngestionManager", "SnowballSource", "AShareIndexSource", "ResearchReportSource"]
