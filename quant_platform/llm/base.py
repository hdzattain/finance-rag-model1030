"""Base abstractions for LLM provider integrations."""
from __future__ import annotations

import abc
from typing import Any, Dict, Optional


class BaseLLMClient(abc.ABC):
    """Abstract base class defining the minimal LLM interface."""

    model: Optional[str] = None

    def __init__(self, token: Optional[str], model: Optional[str] = None) -> None:
        self.token = token
        if model is not None:
            self.model = model

    @abc.abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text for the given ``prompt`` using provider specific APIs."""


class DummyLLMClient(BaseLLMClient):
    """Fallback client used when provider credentials are unavailable."""

    def generate(self, prompt: str, **kwargs: Any) -> str:  # type: ignore[override]
        suffix = kwargs.get("suffix", "")
        return f"[dummy-response]{prompt}{suffix}"[:512]


def ensure_token_available(token: Optional[str], provider_name: str) -> None:
    """Raise a helpful error when the provider token is missing."""

    if not token:
        raise RuntimeError(
            f"Missing token for provider '{provider_name}'. Set the environment variable or "
            "update :class:`PlatformConfig`."
        )
