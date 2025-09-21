"""Integration layer for agentic assistants (e.g. UI-TARS)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class AgentCapability:
    name: str
    description: str
    endpoint: str


@dataclass
class AgentRegistry:
    """Register agent assistants and expose their capabilities."""

    agents: Dict[str, List[AgentCapability]]

    def list_agents(self) -> Dict[str, List[str]]:
        return {name: [cap.name for cap in capabilities] for name, capabilities in self.agents.items()}

    def get_capability(self, agent_name: str, capability: str) -> AgentCapability:
        for cap in self.agents.get(agent_name, []):
            if cap.name == capability:
                return cap
        raise KeyError(f"Capability {capability} not found for agent {agent_name}")


DEFAULT_AGENT_REGISTRY = AgentRegistry(
    agents={
        "ui-tars": [
            AgentCapability(
                name="browser_automation",
                description="在受控浏览器中执行自动化操作，用于验证码、人机验证。",
                endpoint="http://ui-tars/api/browser",
            ),
            AgentCapability(
                name="form_filling",
                description="指导用户完成复杂表单与风控提交流程。",
                endpoint="http://ui-tars/api/forms",
            ),
        ],
    }
)


__all__ = ["AgentRegistry", "AgentCapability", "DEFAULT_AGENT_REGISTRY"]
