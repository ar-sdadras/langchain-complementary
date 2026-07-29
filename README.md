# `langcomp` (LangChain-Complementary Framework)

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![LangGraph Compatible](https://img.shields.io/badge/LangGraph-100%25%20Compatible-green.svg)](https://docs.langchain.com/oss/python/langgraph/overview)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**`langcomp`** is an elegant, developer-friendly, and high-performance complementary framework built on top of [LangChain](https://docs.langchain.com), [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview), and [DeepAgents](https://docs.langchain.com/oss/python/deepagents/overview). 

It addresses common developer friction points in the LangChain ecosystem—eliminating verbose graph wiring, simplifying multi-agent swarm delegation, providing automatic context token compression, adding robust tool execution guardrails, and enabling zero-cloud local graph visualization and E2E unit testing.

---

## 🌟 Key Features

1. **Declarative Agent Blueprint (`AgentBuilder`, `@agent`)**
   - Define nodes, tools, and execution flows in concise, Pythonic code.
   - Zero boilerplate TypedDict or manual reducer code.
   - 100% compatible with native `LangGraph` runtimes and `LangSmith` tracing.

2. **Smart Swarm & Subagent Pool (`SwarmPool`)**
   - Register subagents with instructions and capability tags.
   - Automatic context-isolated subagent tools for multi-agent delegation without context window bloat.

3. **Automatic Context & Memory Engine (`ContextBuffer`, `AutoSummarizer`)**
   - Prevents LLM context overflow errors.
   - Automatic sliding-window message trimming and background conversation summarization.

4. **Tool Guardrails & Approval Gates (`ToolGuard`, `ApprovalGate`)**
   - Automatic retries, fallback outputs, and schema validation for tools.
   - Simplified 1-line Human-In-The-Loop approval gates.

5. **Local DevTools & Visualizer (`GraphVisualizer`, `DryRunner`)**
   - Zero-dependency ASCII and Mermaid graph diagram generator.
   - Dry-run step runner for offline testing of agent node state transitions without API calls.

---

## 📦 Installation

```bash
pip install -e .
```

---

## 🚀 Quickstart

```python
from langcomp import AgentBuilder, SmartState
from langchain_core.messages import AIMessage

# Define custom node functions effortlessly
def analyze_node(state):
    query = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"Analyzed: {query}")]}

# Build agent with fluent API
agent = (
    AgentBuilder("DataAnalyzer")
    .add_node("analyze", analyze_node)
    .compile()
)

result = agent.invoke("Analyze quarterly revenue metrics.")
print(result["messages"][-1].content)
```

---

## 📄 License

MIT License. Developed by AR_S.DADRAS.
