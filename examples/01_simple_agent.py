"""
Example 01: Simple Declarative Agent with langcomp.
Demonstrates building stateful agents without graph ceremony.
"""

from langchain_core.messages import AIMessage
from langcomp import AgentBuilder, GraphVisualizer


def step_analyze(state):
    query = state["messages"][-1].content
    print(f"[Step 1: Analyze] Query received: '{query}'")
    return {"messages": [AIMessage(content=f"Analysis complete for: '{query}'")]}


def step_summarize(state):
    last_msg = state["messages"][-1].content
    print(f"[Step 2: Summarize] Summarizing: '{last_msg}'")
    return {"messages": [AIMessage(content=f"Final Report: {last_msg}")]}


def main():
    print("=== langcomp Example 01: Declarative Agent ===")

    # Construct multi-node agent with fluent syntax
    agent = (
        AgentBuilder("WorkflowAgent")
        .add_node("analyze", step_analyze)
        .add_node("summarize", step_summarize)
        .compile()
    )

    # Render Mermaid diagram
    print("\n--- Agent Mermaid Graph ---")
    print(GraphVisualizer.to_mermaid(agent))

    # Invoke agent
    print("\n--- Invoking Agent ---")
    result = agent.invoke("Market trend analysis Q3")
    
    print("\n--- Execution History ---")
    for msg in result["messages"]:
        print(f"[{msg.__class__.__name__}]: {msg.content}")


if __name__ == "__main__":
    main()
