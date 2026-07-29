# Chapter 01: Getting Started & Core Agents

In this chapter, you will learn how to install `langcomp` and build your first declarative agent using `AgentBuilder`, `@agent`, and `SmartState`.

---

## 🛠️ Installation

Install `langcomp` directly in your Python environment:

```bash
pip install -e .
```

Ensure your dependencies (`langchain-core`, `langgraph`, `pydantic`) are updated:

```bash
pip install --upgrade langchain-core langgraph pydantic
```

---

## 🧩 1. The `SmartState` Abstraction

In standard LangGraph, defining state requires writing verbose `TypedDict` schemas with custom reducers:

```python
# Standard LangGraph (Verbose)
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    custom_field: str
```

With `langcomp.SmartState`, state schemas are generated dynamically and support input payload normalization (strings, dicts, message objects):

```python
# langcomp (Concise)
from langcomp import SmartState

# Create schema with extra custom fields
schema = SmartState.create_schema(extra_fields={"custom_field": str})

# Normalize inputs seamlessly
messages = SmartState.normalize_messages([
    "User query string",
    {"role": "assistant", "content": "AI response"}
])
```

---

## 🏗️ 2. Building Agents with `AgentBuilder`

`AgentBuilder` provides a fluent interface for creating custom node chains or LLM ReAct loops without manual graph wiring.

### Example: Multi-Step Processing Agent

```python
from langchain_core.messages import AIMessage
from langcomp import AgentBuilder

# Define node functions
def extract_keywords(state):
    query = state["messages"][-1].content
    keywords = [w for w in query.split() if len(w) > 4]
    return {"messages": [AIMessage(content=f"Extracted keywords: {keywords}")]}

def generate_summary(state):
    last_msg = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"Summary Report: {last_msg}")]}

# Build and compile agent
agent = (
    AgentBuilder("KeywordExtractorAgent")
    .add_node("extract", extract_keywords)
    .add_node("summarize", generate_summary)
    .compile()
)

# Invoke agent
result = agent.invoke("Analyze machine learning deployment architecture")
print(result["messages"][-1].content)
```

> [!TIP]
> If you add multiple nodes without explicitly specifying edges, `AgentBuilder` automatically wires them sequentially: `START -> node_1 -> node_2 -> ... -> END`.

---

## 🎨 3. Using the `@agent` Decorator

For single-node operations or quick agent functions, use the `@agent` decorator:

```python
from langcomp import agent
from langchain_core.messages import AIMessage

@agent(name="QuickAnalyzer")
def quick_analyzer_node(state):
    text = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"Processed: {text.upper()}")]}

# The decorated function is now a compiled Agent instance!
result = quick_analyzer_node.invoke("hello world")
print(result["messages"][-1].content)  # Output: PROCESSED: HELLO WORLD
```

---

## 📌 Summary Checklist

- [x] Use `SmartState` for input payload normalization.
- [x] Use `AgentBuilder` for fluent multi-node agent assembly.
- [x] Use `@agent` for quick decorator-based agent definitions.
