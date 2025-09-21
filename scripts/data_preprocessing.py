"""Data preprocessing helpers for feeding the RAG knowledge base."""
from __future__ import annotations

import json
from pathlib import Path

from quant_platform import DataIngestionManager, PlatformConfig

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)


class FileSink:
    """Simple sink storing ingested documents locally."""

    def __init__(self, filename: str) -> None:
        self.filename = filename

    def ingest(self, documents: list[dict]) -> None:
        path = OUTPUT_DIR / self.filename
        path.write_text(
            "\n".join(json.dumps(doc, ensure_ascii=False) for doc in documents),
            encoding="utf-8",
        )
        print(f"Exported {len(documents)} documents to {path}")


def main() -> None:
    config = PlatformConfig()
    ingestion = DataIngestionManager(config=config.data_sources, sink=FileSink("ingested.jsonl"))
    ingestion.ingest_all(["SH000001"], ["SH000300"], ["宏观策略"])


if __name__ == "__main__":
    main()
