"""Adapters for third-party backtesting platforms."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Protocol

import logging

LOGGER = logging.getLogger(__name__)


class BacktestPlatform(Protocol):
    """Protocol representing a backtesting platform adapter."""

    name: str

    def run(self, strategy_code: str, params: dict) -> dict:
        ...


@dataclass
class ExternalPlatformAdapter:
    """Generic adapter that proxies to external platform APIs."""

    name: str
    token: str

    def run(self, strategy_code: str, params: dict) -> dict:
        if not self.token:
            raise RuntimeError(f"Token for platform {self.name} missing")
        LOGGER.info("Submitting backtest to %s with params %s", self.name, params)
        # Placeholder: integration with vendor SDK/API would happen here.
        return {"platform": self.name, "status": "submitted", "params": params}


@dataclass
class BacktestPlatformRegistry:
    """Maintain a registry of available platform adapters."""

    adapters: Dict[str, BacktestPlatform]

    @classmethod
    def from_tokens(cls, tokens: Dict[str, str]) -> "BacktestPlatformRegistry":
        adapters = {
            name: ExternalPlatformAdapter(name=name, token=token)
            for name, token in tokens.items()
            if token
        }
        return cls(adapters=adapters)

    def run(self, platform: str, strategy_code: str, params: dict) -> dict:
        adapter = self.adapters.get(platform)
        if adapter is None:
            raise KeyError(f"Platform {platform} not configured")
        return adapter.run(strategy_code, params)


__all__ = ["BacktestPlatformRegistry", "ExternalPlatformAdapter"]
