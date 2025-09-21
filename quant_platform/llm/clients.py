"""Provider specific LLM client implementations."""
from __future__ import annotations

from typing import Any, Dict, Optional

import json
import logging

import requests

from .base import BaseLLMClient, DummyLLMClient, ensure_token_available

LOGGER = logging.getLogger(__name__)


class OpenAIClient(BaseLLMClient):
    """Wrapper around the OpenAI completion API."""

    model = "gpt-4o-mini"
    api_base = "https://api.openai.com/v1/chat/completions"

    def generate(self, prompt: str, **kwargs: Any) -> str:  # type: ignore[override]
        ensure_token_available(self.token, "openai")
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.2),
        }
        try:
            response = requests.post(self.api_base, headers=headers, data=json.dumps(payload), timeout=60)
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - network path
            LOGGER.warning("OpenAI request failed: %s", exc)
            return DummyLLMClient(token=None).generate(prompt)
        data = response.json()
        return data["choices"][0]["message"]["content"]


class AnthropicClient(BaseLLMClient):
    """Wrapper for Anthropic's Claude completion API."""

    model = "claude-3-sonnet-20240229"
    api_base = "https://api.anthropic.com/v1/messages"

    def generate(self, prompt: str, **kwargs: Any) -> str:  # type: ignore[override]
        ensure_token_available(self.token, "anthropic")
        headers = {
            "x-api-key": self.token or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": kwargs.get("model", self.model),
            "max_tokens": kwargs.get("max_tokens", 1024),
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            response = requests.post(self.api_base, headers=headers, data=json.dumps(payload), timeout=60)
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - network path
            LOGGER.warning("Anthropic request failed: %s", exc)
            return DummyLLMClient(token=None).generate(prompt)
        data = response.json()
        return data.get("content", [{}])[0].get("text", "")


class DeepSeekClient(BaseLLMClient):
    """Client for DeepSeek's completion endpoint."""

    model = "deepseek-chat"
    api_base = "https://api.deepseek.com/chat/completions"

    def generate(self, prompt: str, **kwargs: Any) -> str:  # type: ignore[override]
        ensure_token_available(self.token, "deepseek")
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            response = requests.post(self.api_base, headers=headers, data=json.dumps(payload), timeout=60)
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover
            LOGGER.warning("DeepSeek request failed: %s", exc)
            return DummyLLMClient(token=None).generate(prompt)
        data = response.json()
        return data["choices"][0]["message"]["content"]


class QwenClient(BaseLLMClient):
    """Tongyi Qianwen client."""

    model = "qwen-plus"
    api_base = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    def generate(self, prompt: str, **kwargs: Any) -> str:  # type: ignore[override]
        ensure_token_available(self.token, "qwen")
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        payload = {
            "model": kwargs.get("model", self.model),
            "input": {
                "messages": [
                    {"role": "system", "content": kwargs.get("system", "You are a helpful assistant.")},
                    {"role": "user", "content": prompt},
                ]
            },
        }
        try:
            response = requests.post(self.api_base, headers=headers, data=json.dumps(payload), timeout=60)
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover
            LOGGER.warning("Qwen request failed: %s", exc)
            return DummyLLMClient(token=None).generate(prompt)
        data = response.json()
        output = data.get("output", {})
        return output.get("text", "") or DummyLLMClient(token=None).generate(prompt)


__all__ = [
    "OpenAIClient",
    "AnthropicClient",
    "DeepSeekClient",
    "QwenClient",
    "DummyLLMClient",
]
