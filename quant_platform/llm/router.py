"""Routing utilities to dynamically select LLM providers."""
from __future__ import annotations

from typing import Dict, Type

from .base import BaseLLMClient, DummyLLMClient
from .clients import AnthropicClient, DeepSeekClient, OpenAIClient, QwenClient

PROVIDERS: Dict[str, Type[BaseLLMClient]] = {
    "openai": OpenAIClient,
    "anthropic": AnthropicClient,
    "deepseek": DeepSeekClient,
    "qwen": QwenClient,
}


def create_client(provider: str, token: str | None = None, model: str | None = None) -> BaseLLMClient:
    """Create a provider specific client."""

    provider = provider.lower()
    client_cls = PROVIDERS.get(provider)
    if client_cls is None:
        return DummyLLMClient(token=token, model=model)
    return client_cls(token=token, model=model)


__all__ = ["create_client", "PROVIDERS"]
