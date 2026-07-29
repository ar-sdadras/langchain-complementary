"""
Local DevTools, Visualization, and Dry-Runner for langcomp framework.
Allows zero-cloud graph inspection, Mermaid export, ASCII visualization, and step dry-running.
"""

from typing import Any, Dict, List, Optional
from langcomp.core.agent import Agent


class GraphVisualizer:
    """
    Renders visual diagrams (Mermaid, ASCII) for any LangGraph or langcomp Agent.
    """

    @classmethod
    def to_mermaid(cls, agent_or_graph: Any) -> str:
        """
        Generate Mermaid diagram markup for the compiled graph.
        """
        graph_obj = agent_or_graph.graph if isinstance(agent_or_graph, Agent) else agent_or_graph
        try:
            # LangGraph compiled graphs have a get_graph() method
            mermaid_str = graph_obj.get_graph().draw_mermaid()
            return mermaid_str
        except Exception:
            return "graph TD;\n    START --> AgentNode;\n    AgentNode --> END;"

    @classmethod
    def to_ascii(cls, agent_or_graph: Any) -> str:
        """
        Generate ASCII box representation of graph structure.
        """
        graph_obj = agent_or_graph.graph if isinstance(agent_or_graph, Agent) else agent_or_graph
        try:
            ascii_str = graph_obj.get_graph().draw_ascii()
            return ascii_str
        except Exception:
            return "[START] ---> [Agent Node] ---> [END]"


class DryRunner:
    """
    Dry-runner engine for testing node state mutations step-by-step without remote API calls.
    """

    def __init__(self, agent_inst: Agent):
        self.agent = agent_inst

    def run_step(self, node_name: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single node logic function directly against a state dictionary.
        """
        # Search for custom node function in internal builder if available
        graph_obj = self.agent.graph
        nodes = getattr(graph_obj, "nodes", {})
        if node_name in nodes:
            node_runnable = nodes[node_name]
            # Invoke node runnable directly
            if hasattr(node_runnable, "invoke"):
                return node_runnable.invoke(current_state)
            elif callable(node_runnable):
                return node_runnable(current_state)

        raise ValueError(f"Node '{node_name}' not found in agent graph.")
