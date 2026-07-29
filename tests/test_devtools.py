"""
Unit tests for langcomp.devtools.visualizer.
"""

from langchain_core.messages import AIMessage
from langcomp.core.agent import AgentBuilder
from langcomp.devtools.visualizer import GraphVisualizer, DryRunner


def test_graph_visualizer_mermaid():
    def node_a(state):
        return {"messages": [AIMessage(content="Node A")]}

    agent = (
        AgentBuilder("VizAgent")
        .add_node("node_a", node_a)
        .compile()
    )

    mermaid_markup = GraphVisualizer.to_mermaid(agent)
    assert isinstance(mermaid_markup, str)
    assert len(mermaid_markup) > 0

    ascii_markup = GraphVisualizer.to_ascii(agent)
    assert isinstance(ascii_markup, str)


def test_dry_runner():
    def step_node(state):
        counter = state.get("counter", 0) + 1
        return {"counter": counter}

    agent = (
        AgentBuilder("DryRunAgent")
        .with_state_schema({"counter": int})
        .add_node("step_node", step_node)
        .compile()
    )

    runner = DryRunner(agent)
    res = runner.run_step("step_node", {"counter": 5})
    assert res["counter"] == 6
