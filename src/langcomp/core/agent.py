"""
Declarative Agent Core for langcomp.
Provides intuitive AgentBuilder and @agent decorators.
"""

from typing import Any, Callable, Dict, List, Optional, Union
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.base import BaseCheckpointSaver

from langcomp.core.state import SmartState


class Agent:
    """
    Wrapper around a compiled LangGraph runnable.
    Provides easy execution (.run(), .stream()) and state inspection.
    """

    def __init__(self, name: str, compiled_graph: Any, state_schema: Any = None):
        self.name = name
        self.graph = compiled_graph
        self.state_schema = state_schema or SmartState.create_schema()

    @classmethod
    def from_runnable(cls, runnable: Any, name: str = "LangChainAgent") -> "Agent":
        """
        Wrap any runnable compiled graph produced by LangChain create_agent() or DeepAgents create_deep_agent().
        """
        return cls(name=name, compiled_graph=runnable)

    def invoke(
        self,
        input_data: Union[str, Dict[str, Any], List[Any]],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke the compiled agent with string prompt, dict state, or message list.
        """
        config = config or {"configurable": {"thread_id": "default"}}
        
        if isinstance(input_data, str):
            payload = {"messages": SmartState.normalize_messages([input_data])}
        elif isinstance(input_data, list):
            payload = {"messages": SmartState.normalize_messages(input_data)}
        elif isinstance(input_data, dict):
            payload = input_data.copy()
            if "messages" in payload and isinstance(payload["messages"], list):
                payload["messages"] = SmartState.normalize_messages(payload["messages"])
        else:
            payload = {"messages": []}

        return self.graph.invoke(payload, config=config)

    async def ainvoke(
        self,
        input_data: Union[str, Dict[str, Any], List[Any]],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Async invoke the agent.
        """
        config = config or {"configurable": {"thread_id": "default"}}
        
        if isinstance(input_data, str):
            payload = {"messages": SmartState.normalize_messages([input_data])}
        elif isinstance(input_data, list):
            payload = {"messages": SmartState.normalize_messages(input_data)}
        elif isinstance(input_data, dict):
            payload = input_data.copy()
            if "messages" in payload and isinstance(payload["messages"], list):
                payload["messages"] = SmartState.normalize_messages(payload["messages"])
        else:
            payload = {"messages": []}

        return await self.graph.ainvoke(payload, config=config)

    def get_state(self, config: Dict[str, Any]) -> Any:
        """
        Retrieve current agent state snapshot for a given thread_id configuration.
        """
        return self.graph.get_state(config)


class AgentBuilder:
    """
    Fluent builder pattern for constructing LangGraph agents without graph ceremony.
    """

    def __init__(self, name: str = "LangCompAgent"):
        self.name = name
        self._model: Optional[Union[BaseLanguageModel, str]] = None
        self._tools: List[Union[BaseTool, Callable]] = []
        self._system_prompt: Optional[str] = None
        self._state_fields: Dict[str, Any] = {}
        self._custom_nodes: Dict[str, Callable] = {}
        self._edges: List[tuple[str, str]] = []
        self._checkpointer: Optional[BaseCheckpointSaver] = None

    def with_model(self, model: Union[BaseLanguageModel, str]) -> "AgentBuilder":
        self._model = model
        return self

    def with_tools(self, tools: List[Union[BaseTool, Callable]]) -> "AgentBuilder":
        self._tools.extend(tools)
        return self

    def with_system_prompt(self, prompt: str) -> "AgentBuilder":
        self._system_prompt = prompt
        return self

    def with_state_schema(self, extra_fields: Dict[str, Any]) -> "AgentBuilder":
        self._state_fields.update(extra_fields)
        return self

    def with_checkpointer(self, checkpointer: BaseCheckpointSaver) -> "AgentBuilder":
        self._checkpointer = checkpointer
        return self

    def add_node(self, name: str, func: Callable) -> "AgentBuilder":
        self._custom_nodes[name] = func
        return self

    def add_edge(self, start_node: str, end_node: str) -> "AgentBuilder":
        self._edges.append((start_node, end_node))
        return self

    def compile(self) -> Agent:
        """
        Compile configuration into a ready-to-run Agent instance.
        """
        state_schema = SmartState.create_schema(extra_fields=self._state_fields)

        # If custom nodes are defined, build a StateGraph
        if self._custom_nodes:
            builder = StateGraph(state_schema)
            for node_name, node_func in self._custom_nodes.items():
                builder.add_node(node_name, node_func)

            if not self._edges:
                node_names = list(self._custom_nodes.keys())
                builder.add_edge(START, node_names[0])
                for i in range(len(node_names) - 1):
                    builder.add_edge(node_names[i], node_names[i + 1])
                builder.add_edge(node_names[-1], END)
            else:
                for start, end in self._edges:
                    builder.add_edge(start, end)

            compiled = builder.compile(checkpointer=self._checkpointer)
            return Agent(name=self.name, compiled_graph=compiled, state_schema=state_schema)

        # Otherwise, build a standard ReAct agent if model is provided
        if self._model is not None:
            compiled = create_react_agent(
                model=self._model,
                tools=self._tools,
                prompt=self._system_prompt,
                checkpointer=self._checkpointer,
            )
            return Agent(name=self.name, compiled_graph=compiled, state_schema=state_schema)

        raise ValueError("AgentBuilder requires either a model or custom nodes to compile.")


def agent(
    name: str = "DecoratedAgent",
    model: Optional[Any] = None,
    tools: Optional[List[Any]] = None,
    system_prompt: Optional[str] = None,
) -> Callable:
    """
    Decorator for quick agent creation from a node function or LLM config.
    """
    def decorator(func_or_class: Any) -> Agent:
        builder = AgentBuilder(name=name)
        if model is not None:
            builder.with_model(model)
        if tools:
            builder.with_tools(tools)
        if system_prompt:
            builder.with_system_prompt(system_prompt)

        if callable(func_or_class) and not isinstance(func_or_class, type):
            # It's a node function
            builder.add_node(name, func_or_class)
            builder.add_edge(START, name)
            builder.add_edge(name, END)

        return builder.compile()

    return decorator
