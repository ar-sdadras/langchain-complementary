# Chapter 02: Multi-Agent Swarms & Subagent Delegation

In this chapter, you will learn how to orchestrate multi-agent swarms using `SwarmPool` and `SubAgent` to achieve clean context isolation.

---

## 🎯 The Context Bloat Problem

In complex multi-agent applications, passing all messages between supervisor and worker agents can quickly exhaust the LLM's context window.

```mermaid
graph LR
    subgraph Bad Approach: Shared Context
        S1[Supervisor] <-->|All Messages| W1[Worker A]
        S1 <-->|All Messages| W2[Worker B]
    end
    
    subgraph Good Approach: Subagent Tool Isolation
        S2[Supervisor] -->|Query| Sub1[Subagent Tool A]
        Sub1 -->|Isolated Context Output| S2
        S2 -->|Query| Sub2[Subagent Tool B]
        Sub2 -->|Isolated Context Output| S2
    end
```

`langcomp.swarm` solves this by converting subagents into context-isolated tools that can be registered in a pool and called dynamically.

---

## 🐝 1. Registering Subagents with `SwarmPool`

`SwarmPool` manages registered subagents and exposes their capabilities as standard LangChain tools.

```python
from langchain_core.messages import AIMessage
from langcomp import AgentBuilder, SwarmPool

# 1. Define specialized worker agents
def researcher_logic(state):
    query = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"Research Findings for '{query}': Found 3 key papers.")]}

def coder_logic(state):
    query = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"Generated Code for '{query}': def solution(): pass")]}

researcher_agent = AgentBuilder("ResearcherAgent").add_node("res", researcher_logic).compile()
coder_agent = AgentBuilder("CoderAgent").add_node("code", coder_logic).compile()

# 2. Instantiate SwarmPool and register subagents
pool = SwarmPool("DevTeamSwarm")

pool.register(
    name="researcher",
    description="Specialized in technical research and paper summaries",
    agent_or_callable=researcher_agent,
    capabilities=["search", "documentation"],
)

pool.register(
    name="programmer",
    description="Specialized in writing and debugging Python code",
    agent_or_callable=coder_agent,
    capabilities=["python", "coding"],
)
```

---

## 🛠️ 2. Exporting Subagent Tools for Supervisor Agents

To let a main supervisor agent invoke subagents dynamically, retrieve tools from the pool:

```python
# Convert all subagents into standard LangChain tools
tools = pool.get_tools()

for t in tools:
    print(f"Tool Name: {t.name}")
    print(f"Description: {t.description}\n")
```

### Invoking a Subagent Tool

```python
research_tool = tools[0]

# Execute subagent tool with task description
result = research_tool.invoke({"task_description": "Summarize attention mechanism in Transformers"})
print(result)
# Output: Research Findings for 'Summarize attention mechanism in Transformers': Found 3 key papers.
```

---

## 💡 3. Interoperability with Modern LangChain `create_agent()` and `DeepAgents`

Modern LangChain 1.x (`create_agent()`) and **DeepAgents** (`create_deep_agent()`) introduce built-in `SubAgentMiddleware` and `CompiledSubAgent` patterns.

`langcomp` provides full native interoperability with both:

### Exporting `langcomp` SubAgents to DeepAgents / LangChain Middleware

```python
from langcomp import SwarmPool, SubAgent

pool = SwarmPool("CrossFrameworkPool")
sub = pool.register(
    name="security_reviewer",
    description="Reviews code for security issues and line-level severity",
    agent_or_callable=my_reviewer_logic,
)

# Export as dictionary compatible with DeepAgents SubAgentMiddleware
deepagents_sub_dict = sub.to_deepagents_subagent_dict()
# Pass directly into DeepAgents or LangChain create_agent():
# agent = create_deep_agent(model="gemini-3.6-flash", subagents=[deepagents_sub_dict])
```

### Wrapping `create_agent()` / `create_deep_agent()` Runnables into `langcomp`

```python
from langchain.agents import create_agent
from langcomp import Agent

# Create an agent using modern LangChain 1.x
lc_agent_runnable = create_agent(
    model="claude-sonnet-4-6",
    tools=[my_tool],
)

# Wrap into langcomp Agent to enable local ASCII/Mermaid visualizers & DryRunner
langcomp_agent = Agent.from_runnable(lc_agent_runnable, name="WrappedLCAgent")
```

---

## 📌 Summary Checklist

- [x] Understand how subagent tool execution prevents supervisor context bloat.
- [x] Register subagents into `SwarmPool` and export them as LangChain tools.
- [x] Export `SubAgent` dicts for modern LangChain `create_agent()` and `DeepAgents` `SubAgentMiddleware`.

