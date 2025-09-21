"""Backtesting layer for Chan-lun strategies and platform integrations."""
from .manager import QuantBacktestManager
from .chan import ChanLunAnalyzer, ChanSegment
from .platforms import BacktestPlatformRegistry

__all__ = ["QuantBacktestManager", "ChanLunAnalyzer", "ChanSegment", "BacktestPlatformRegistry"]
