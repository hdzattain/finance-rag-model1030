"""Frontend architecture blueprint combining React and Vue modules."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class FrontendModule:
    name: str
    framework: str
    description: str


@dataclass
class FrontendArchitecturePlanner:
    """Describe the hybrid React + Vue frontend layout."""

    def login_page_blueprint(self) -> Dict[str, List[FrontendModule]]:
        return {
            "shell": [
                FrontendModule(
                    name="AuthShell",
                    framework="React",
                    description="负责全局状态、路由守卫和与后端的 token 交互。",
                ),
            ],
            "widgets": [
                FrontendModule(
                    name="LoginForm",
                    framework="Vue",
                    description="使用 Composition API 构建的表单组件，支持验证码和多因素认证。",
                ),
                FrontendModule(
                    name="ProviderSelector",
                    framework="React",
                    description="展示可选的大模型和回测平台，通过 context 共享选择状态。",
                ),
                FrontendModule(
                    name="AgentStatusPanel",
                    framework="Vue",
                    description="实时展示 agent 任务进度，使用 WebSocket 获取状态更新。",
                ),
            ],
        }


__all__ = ["FrontendArchitecturePlanner", "FrontendModule"]
