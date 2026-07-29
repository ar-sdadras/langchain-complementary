"""
Example 02: Multi-Agent Swarm with langcomp.
Demonstrates SwarmPool subagent registration and context-isolated subagent tool delegation.
"""

from langchain_core.messages import AIMessage
from langcomp import AgentBuilder, SwarmPool


def research_agent_node(state):
    query = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"Research Findings for '{query}': Found 3 key tech insights.")]}


def math_agent_node(state):
    query = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"Math Result for '{query}': Computed value = 42.0")]}


def main():
    print("=== langcomp Example 02: Multi-Agent Swarm ===")

    # Create subagent instances
    research_agent = AgentBuilder("ResearchAgent").add_node("res", research_agent_node).compile()
    math_agent = AgentBuilder("MathAgent").add_node("math", math_agent_node).compile()

    # Register in SwarmPool
    pool = SwarmPool("TechSwarm")
    pool.register(
        name="researcher",
        description="Specialized in deep technical research and paper summaries",
        agent_or_callable=research_agent,
        capabilities=["web_research", "paper_summary"],
    )
    pool.register(
        name="calculator",
        description="Specialized in mathematical computations and data calculations",
        agent_or_callable=math_agent,
        capabilities=["math", "statistics"],
    )

    print("\n--- Registered Swarm Subagents ---")
    for sub in pool.list_subagents():
        print(f"- {sub['name']}: {sub['description']} (Capabilities: {sub['capabilities']})")

    # Retrieve LangChain-compatible tools from swarm
    tools = pool.get_tools()
    print(f"\nGenerated {len(tools)} subagent tools for supervisor delegation:")
    for t in tools:
        print(f"Tool Name: {t.name} | Description: {t.description}")

    # Test direct subagent tool call
    print("\n--- Delegating Task to Subagent 'researcher' ---")
    res_tool = tools[0]
    result = res_tool.invoke({"task_description": "Analyze LLM context compression algorithms"})
    print(f"Subagent Response:\n{result}")


if __name__ == "__main__":
    main()
