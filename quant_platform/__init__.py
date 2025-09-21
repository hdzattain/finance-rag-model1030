"""Quant strategy platform package exposing layered architecture components."""
from .config import PlatformConfig
from .llm import create_client
from .rag import AgenticRAGPipeline
from .ingestion import DataIngestionManager
from .backtesting import QuantBacktestManager
from .research import ResearchCoordinator
from .frontend import FrontendArchitecturePlanner
from .agents import DEFAULT_AGENT_REGISTRY
from .virtualization import VirtualLoginSandbox
from .architecture_layer import ArchitectureOptimiser
from .hardware import HardwareAdapter

__all__ = [
    "PlatformConfig",
    "create_client",
    "AgenticRAGPipeline",
    "DataIngestionManager",
    "QuantBacktestManager",
    "ResearchCoordinator",
    "FrontendArchitecturePlanner",
    "DEFAULT_AGENT_REGISTRY",
    "VirtualLoginSandbox",
    "ArchitectureOptimiser",
    "HardwareAdapter",
]
