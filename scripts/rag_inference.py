"""Command line helper to run the agentic RAG pipeline."""
from __future__ import annotations

import os

from quant_platform import AgenticRAGPipeline, PlatformConfig, create_client
from quant_platform.llm import DummyLLMClient

SAMPLE_DOCS = [
    {
        "source": "internal-note",
        "text": "上证指数在30分钟级别形成三笔向上，关注前高压力位。",
    },
    {
        "source": "strategy",
        "text": "结合缠论中枢震荡，建议在中枢上沿进行分批减仓，使用5日均线作为辅助。",
    },
]


def build_pipeline() -> AgenticRAGPipeline:
    config = PlatformConfig()
    provider = os.getenv("LLM_PROVIDER", "openai")
    token = getattr(config.llm_tokens, provider, None)
    try:
        llm = create_client(provider, token=token)
        if not token:
            llm = DummyLLMClient(token=None)
    except Exception:
        llm = DummyLLMClient(token=None)
    pipeline = AgenticRAGPipeline(config=config, llm_client=llm)
    pipeline.ingest(SAMPLE_DOCS)
    return pipeline


def main() -> None:
    pipeline = build_pipeline()
    result = pipeline.run("如何基于缠论构建趋势追踪策略？", rounds=1)
    print(result["answer"])


if __name__ == "__main__":
    main()
