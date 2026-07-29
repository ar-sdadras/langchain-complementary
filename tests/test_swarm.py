"""
Unit tests for langcomp.swarm.pool.
"""

from langchain_core.messages import AIMessage
from langcomp.core.agent import AgentBuilder
from langcomp.swarm.pool import SwarmPool, SubAgent


def test_swarm_pool_registration_and_execution():
    pool = SwarmPool("TestPool")

    def dummy_subagent_func(query: str) -> str:
        return f"Processed query: {query}"

    sub = pool.register(
        name="researcher",
        description="Researches information",
        agent_or_callable=dummy_subagent_func,
        capabilities=["research", "search"],
    )

    assert sub.name == "researcher"
    assert "researcher" in pool.subagents

    output = sub.run("quantum computing")
    assert "Processed query: quantum computing" in output

    tools = pool.get_tools()
    assert len(tools) == 1
    assert tools[0].name == "researcher"


def test_subagent_wrapping_agent():
    def agent_node(state):
        return {"messages": [AIMessage(content="Agent output content")]}

    sub_agent_inst = (
        AgentBuilder("SubAgentCore")
        .add_node("step", agent_node)
        .compile()
    )

    pool = SwarmPool("AgentPool")
    sub = pool.register(
        name="agent_worker",
        description="Worker agent",
        agent_or_callable=sub_agent_inst,
    )

    tool_inst = sub.as_tool()
    res = tool_inst.invoke({"task_description": "do work"})
    assert res == "Agent output content"
