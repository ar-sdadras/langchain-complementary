"""
Swarm & Subagent Router for langcomp framework.
Enables clean multi-agent orchestration, context isolation, and tool-based subagent delegation.
"""

from typing import Any, Callable, Dict, List, Optional, Union
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field, ConfigDict

from langcomp.core.agent import Agent


class SubAgent(BaseModel):
    """
    Subagent specification wrapping an Agent or callable.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    description: str
    capabilities: List[str] = Field(default_factory=list)
    agent_instance: Any

    def run(self, query: str, thread_id: Optional[str] = None) -> str:
        """
        Execute the subagent with a isolated context query.
        """
        config = {"configurable": {"thread_id": thread_id or f"subagent_{self.name}"}}
        if isinstance(self.agent_instance, Agent):
            res = self.agent_instance.invoke(query, config=config)
            msgs = res.get("messages", [])
            if msgs:
                last_msg = msgs[-1]
                return last_msg.content if isinstance(last_msg, BaseMessage) else str(last_msg)
            return "Subagent finished with no output messages."
        elif callable(self.agent_instance):
            res = self.agent_instance(query)
            return str(res)
        else:
            raise ValueError(f"Unsupported subagent instance type: {type(self.agent_instance)}")

    def as_tool(self) -> BaseTool:
        """
        Convert this subagent into a LangChain tool for standard tool-calling agent delegation.
        """
        sub_name = self.name
        sub_desc = self.description
        sub_run = self.run

        @tool(sub_name, description=f"Delegate task to subagent '{sub_name}': {sub_desc}")
        def subagent_tool(task_description: str) -> str:
            """Subagent tool wrapper."""
            return sub_run(task_description)

        return subagent_tool


class SwarmPool:
    """
    Manager pool for multi-agent swarms.
    """

    def __init__(self, name: str = "DefaultSwarmPool"):
        self.name = name
        self.subagents: Dict[str, SubAgent] = {}

    def register(
        self,
        name: str,
        description: str,
        agent_or_callable: Any,
        capabilities: Optional[List[str]] = None,
    ) -> SubAgent:
        """
        Register a subagent in the swarm pool.
        """
        subagent = SubAgent(
            name=name,
            description=description,
            capabilities=capabilities or [],
            agent_instance=agent_or_callable,
        )
        self.subagents[name] = subagent
        return subagent

    def get_tools(self) -> List[BaseTool]:
        """
        Get all registered subagents converted as LangChain tools for supervisor delegation.
        """
        return [sub.as_tool() for sub in self.subagents.values()]

    def list_subagents(self) -> List[Dict[str, Any]]:
        """
        Return metadata list of registered subagents.
        """
        return [
            {
                "name": sub.name,
                "description": sub.description,
                "capabilities": sub.capabilities,
            }
            for sub in self.subagents.values()
        ]
