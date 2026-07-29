"""
SmartState management for langcomp framework.
Eliminates boilerplate TypedDict and reducer definitions for LangGraph.
"""

from typing import Any, Dict, List, Optional, Type, Union, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph.message import add_messages


class SmartState:
    """
    Helper for dynamically building LangGraph state schemas without boilerplate.
    Provides standard message accumulation and typed state dictionary support.
    """

    @classmethod
    def create_schema(
        cls,
        extra_fields: Optional[Dict[str, Any]] = None,
        messages_key: str = "messages",
    ) -> Type:
        """
        Dynamically create a TypedDict class compatible with LangGraph.
        
        Args:
            extra_fields: Dictionary mapping state keys to their type hints or default initializers.
            messages_key: Key name used for conversation history messages.
            
        Returns:
            A dynamically generated TypedDict class.
        """
        annotations: Dict[str, Any] = {
            messages_key: Annotated[List[BaseMessage], add_messages]
        }
        
        if extra_fields:
            for key, val_type in extra_fields.items():
                annotations[key] = val_type
                
        # Construct dynamically
        namespace = {"__annotations__": annotations}
        return type("GeneratedSmartState", (dict,), namespace)

    @staticmethod
    def normalize_messages(messages: List[Union[BaseMessage, Dict[str, str], str]]) -> List[BaseMessage]:
        """
        Convert dicts or raw strings into standard LangChain BaseMessage instances.
        """
        normalized: List[BaseMessage] = []
        for msg in messages:
            if isinstance(msg, BaseMessage):
                normalized.append(msg)
            elif isinstance(msg, dict):
                role = msg.get("role", "user").lower()
                content = msg.get("content", "")
                if role in ("user", "human"):
                    normalized.append(HumanMessage(content=content))
                elif role in ("assistant", "ai"):
                    normalized.append(AIMessage(content=content))
                elif role in ("system",):
                    normalized.append(SystemMessage(content=content))
                else:
                    normalized.append(HumanMessage(content=content))
            elif isinstance(msg, str):
                normalized.append(HumanMessage(content=msg))
        return normalized
