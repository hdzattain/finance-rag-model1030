"""Hardware adaptation strategies for heterogeneous environments."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ..config import HardwareProfile


@dataclass
class HardwareAdapter:
    """Select optimal model variants and batch sizes based on hardware."""

    profile: HardwareProfile

    def select_embedding_batch_size(self) -> int:
        if self.profile.gpu_memory_gb and self.profile.gpu_memory_gb >= 24:
            return 64
        if self.profile.gpu_memory_gb and self.profile.gpu_memory_gb >= 12:
            return 32
        if self.profile.cpu_cores and self.profile.cpu_cores >= 16:
            return 16
        return 8

    def choose_llm_model(self) -> str:
        accelerator = (self.profile.accelerator or "cpu").lower()
        if "h100" in accelerator or "a100" in accelerator:
            return "gpt-4o"
        if "v100" in accelerator or "l40" in accelerator:
            return "gpt-4o-mini"
        return "qwen-plus"

    def summary(self) -> Dict[str, str | int | None]:
        return {
            "accelerator": self.profile.accelerator,
            "gpu_memory_gb": self.profile.gpu_memory_gb,
            "cpu_cores": self.profile.cpu_cores,
            "embedding_batch_size": self.select_embedding_batch_size(),
            "llm_model": self.choose_llm_model(),
        }


__all__ = ["HardwareAdapter"]
