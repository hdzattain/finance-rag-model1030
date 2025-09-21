"""Virtual container sandbox for handling manual login workflows."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LoginTask:
    url: str
    instructions: str
    completed: bool = False


@dataclass
class VirtualLoginSandbox:
    """Maintain simulated browser sessions requiring human interaction."""

    tasks: List[LoginTask] = field(default_factory=list)

    def enqueue(self, url: str, instructions: str) -> None:
        self.tasks.append(LoginTask(url=url, instructions=instructions))

    def list_pending(self) -> List[Dict[str, str]]:
        return [
            {"url": task.url, "instructions": task.instructions}
            for task in self.tasks
            if not task.completed
        ]

    def mark_completed(self, url: str) -> None:
        for task in self.tasks:
            if task.url == url:
                task.completed = True
                return
        raise KeyError(f"Task for {url} not found")


__all__ = ["VirtualLoginSandbox", "LoginTask"]
