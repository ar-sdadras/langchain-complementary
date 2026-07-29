"""
Unit tests for DeepAgents and modern LangChain create_agent interop.
"""

from langchain_core.messages import AIMessage
from langcomp import Agent, AgentBuilder, SwarmPool, SubAgent


def test_agent_from_runnable():
    def dummy_runnable_invoke(payload, config=None):
        return {"messages": [AIMessage(content="Response from create_agent runnable")]}

    class MockRunnable:
        def invoke(self, payload, config=None):
            return dummy_runnable_invoke(payload, config)

    mock_runnable = MockRunnable()
    agent = Agent.from_runnable(mock_runnable, name="ModernLangChainAgent")

    res = agent.invoke("Test query")
    assert res["messages"][0].content == "Response from create_agent runnable"


def test_subagent_deepagents_dict_export():
    pool = SwarmPool("DeepAgentsPool")
    sub = pool.register(
        name="reviewer",
        description="Security code reviewer",
        agent_or_callable=lambda q: "Clean code",
        capabilities=["security", "code"],
    )

    deep_dict = sub.to_deepagents_subagent_dict()
    assert deep_dict["name"] == "reviewer"
    assert deep_dict["description"] == "Security code reviewer"
    assert "reviewer" in deep_dict["system_prompt"]
