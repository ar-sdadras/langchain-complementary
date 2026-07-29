# Chapter 05: DevTools, Visualization & Offline Testing

In this chapter, you will learn how to inspect agent topologies visually using `GraphVisualizer` and how to unit test state transitions locally using `DryRunner`.

---

## 📊 1. Visualizing Graphs with `GraphVisualizer`

Understanding graph topologies and node connections is crucial for debugging complex agent workflows. `GraphVisualizer` exports graph structures directly into **Mermaid** diagrams or **ASCII** boxes without requiring cloud tracing tools.

```python
from langchain_core.messages import AIMessage
from langcomp import AgentBuilder, GraphVisualizer

# Define a multi-step agent
def step_one(state):
    return {"messages": [AIMessage(content="Step 1 complete")]}

def step_two(state):
    return {"messages": [AIMessage(content="Step 2 complete")]}

agent = (
    AgentBuilder("PipelineAgent")
    .add_node("step_one", step_one)
    .add_node("step_two", step_two)
    .compile()
)

# 1. Generate Mermaid Diagram Markup
mermaid_code = GraphVisualizer.to_mermaid(agent)
print("=== Mermaid Diagram ===")
print(mermaid_code)

# 2. Generate ASCII Box Representation
ascii_code = GraphVisualizer.to_ascii(agent)
print("\n=== ASCII Representation ===")
print(ascii_code)
```

> [!TIP]
> You can embed the generated Mermaid code directly into GitHub markdown files, Notion documents, or documentation sites for automatic visual rendering!

---

## 🧪 2. Offline Unit Testing with `DryRunner`

When writing unit tests for custom node functions, invoking LLMs over the network introduces latency, cost, and non-determinism.

`DryRunner` allows executing individual graph nodes step-by-step against mock state dictionaries locally.

```python
from langcomp import AgentBuilder, DryRunner

# Node logic function under test
def calculate_score_node(state):
    items = state.get("items", [])
    score = sum(len(item) for item in items)
    return {"score": score}

# Build agent with custom state schema
agent = (
    AgentBuilder("ScoringAgent")
    .with_state_schema({"items": list, "score": int})
    .add_node("calculate_score", calculate_score_node)
    .compile()
)

# Test node in isolation using DryRunner
runner = DryRunner(agent)

mock_initial_state = {"items": ["apple", "banana", "cherry"]}
result_state = runner.run_step("calculate_score", mock_initial_state)

print(f"Calculated Score: {result_state['score']}")  # Expected: 5 + 6 + 6 = 17
assert result_state["score"] == 17
print("Unit Test Passed!")
```

---

## 📝 3. Writing Pytest Unit Tests for Agents

Here is a template for writing clean, fast unit tests for `langcomp` agents using `pytest`:

```python
import pytest
from langchain_core.messages import AIMessage
from langcomp import AgentBuilder, DryRunner

@pytest.fixture
def sample_agent():
    def transform_node(state):
        text = state["messages"][-1].content
        return {"messages": [AIMessage(content=text.upper())]}

    return AgentBuilder("TestAgent").add_node("transform", transform_node).compile()

def test_agent_invocation(sample_agent):
    result = sample_agent.invoke("hello")
    assert result["messages"][-1].content == "HELLO"

def test_dry_run_step(sample_agent):
    runner = DryRunner(sample_agent)
    res = runner.run_step("transform", {"messages": [AIMessage(content="unit test")]})
    assert res["messages"][-1].content == "UNIT TEST"
```

---

## 🎉 Tutorial Suite Wrap-Up

Congratulations! You have completed the `langcomp` tutorial suite. You now know how to:
- Build declarative agents using `AgentBuilder` and `@agent`.
- Orchestrate multi-agent swarms using `SwarmPool`.
- Manage context limits using `ContextBuffer` and `AutoSummarizer`.
- Protect tools using `ToolGuard` and `ApprovalGate`.
- Visualize and unit test agent graphs using `GraphVisualizer` and `DryRunner`.
