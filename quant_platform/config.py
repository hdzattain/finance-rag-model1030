"""Configuration utilities for the quant strategy platform."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional
import os


@dataclass
class QdrantConfig:
    """Configuration for Qdrant vector database."""

    host: str = field(default_factory=lambda: os.getenv("QDRANT_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("QDRANT_PORT", "6333")))
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("QDRANT_API_KEY"))
    collection_name: str = field(
        default_factory=lambda: os.getenv("QDRANT_COLLECTION", "finance_rag_documents")
    )


@dataclass
class LLMProviderTokens:
    """Access tokens for supported LLM providers."""

    openai: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic: Optional[str] = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    deepseek: Optional[str] = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY"))
    qwen: Optional[str] = field(default_factory=lambda: os.getenv("QWEN_API_KEY"))


@dataclass
class DataSourceConfig:
    """Configuration for external financial data sources."""

    snowball_cookie: Optional[str] = field(
        default_factory=lambda: os.getenv("SNOWBALL_COOKIE")
    )  # 雪球
    research_api_token: Optional[str] = field(default_factory=lambda: os.getenv("RESEARCH_API_TOKEN"))
    aws_secret_name: Optional[str] = field(default_factory=lambda: os.getenv("AWS_SECRET_NAME"))


@dataclass
class BacktestPlatformConfig:
    """Tokens for accessing third-party backtesting services."""

    platform_tokens: Dict[str, str] = field(
        default_factory=lambda: {
            "joinquant": os.getenv("JOINQUANT_TOKEN", ""),
            "ricequant": os.getenv("RICEQUANT_TOKEN", ""),
            "bigquant": os.getenv("BIGQUANT_TOKEN", ""),
        }
    )


@dataclass
class HardwareProfile:
    """Hardware adaptation profile."""

    accelerator: Optional[str] = field(default_factory=lambda: os.getenv("ACCELERATOR_TYPE"))
    gpu_memory_gb: Optional[int] = field(
        default_factory=lambda: int(os.getenv("GPU_MEMORY_GB", "0")) if os.getenv("GPU_MEMORY_GB") else None
    )
    cpu_cores: Optional[int] = field(
        default_factory=lambda: int(os.getenv("CPU_CORES", "0")) if os.getenv("CPU_CORES") else None
    )


@dataclass
class PlatformConfig:
    """Master configuration object aggregating all subsystems."""

    llm_tokens: LLMProviderTokens = field(default_factory=LLMProviderTokens)
    qdrant: QdrantConfig = field(default_factory=QdrantConfig)
    data_sources: DataSourceConfig = field(default_factory=DataSourceConfig)
    backtest: BacktestPlatformConfig = field(default_factory=BacktestPlatformConfig)
    hardware: HardwareProfile = field(default_factory=HardwareProfile)


__all__ = [
    "PlatformConfig",
    "LLMProviderTokens",
    "QdrantConfig",
    "DataSourceConfig",
    "BacktestPlatformConfig",
    "HardwareProfile",
]
