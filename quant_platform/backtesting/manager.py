"""Backtesting manager orchestrating Chan-lun strategies and platform integrations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd

from ..config import BacktestPlatformConfig
from .chan import ChanLunAnalyzer
from .platforms import BacktestPlatformRegistry


@dataclass
class QuantBacktestManager:
    """Coordinate local Chan-lun strategy evaluation and remote submissions."""

    platform_config: BacktestPlatformConfig
    analyzer: ChanLunAnalyzer = ChanLunAnalyzer()
    registry: BacktestPlatformRegistry | None = None

    def __post_init__(self) -> None:
        if self.registry is None:
            self.registry = BacktestPlatformRegistry.from_tokens(self.platform_config.platform_tokens)

    def backtest_local(self, market_data: pd.DataFrame, initial_capital: float = 1_000_000.0) -> Dict[str, float]:
        """Run a simple Chan-lun based backtest locally."""

        signals = self.analyzer.generate_signals(market_data)
        returns = market_data["close"].pct_change().fillna(0)
        strategy_returns = returns * signals.shift(1).fillna(0)
        equity_curve = (1 + strategy_returns).cumprod() * initial_capital
        return {
            "final_equity": float(equity_curve.iloc[-1]),
            "cumulative_return": float(equity_curve.iloc[-1] / initial_capital - 1),
            "max_drawdown": float((equity_curve.cummax() - equity_curve).max() / equity_curve.cummax().max()),
        }

    def submit_remote(self, platform: str, strategy_code: str, params: Optional[dict] = None) -> Dict[str, str]:
        if params is None:
            params = {}
        if self.registry is None:
            raise RuntimeError("Backtest platform registry not configured")
        return self.registry.run(platform, strategy_code, params)


__all__ = ["QuantBacktestManager"]
