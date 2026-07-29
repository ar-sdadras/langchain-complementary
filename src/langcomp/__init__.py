"""
langcomp: LangChain-Complementary Framework
High-level, developer-friendly abstractions on top of LangChain, LangGraph, and DeepAgents.
"""

__version__ = "0.1.0"

from langcomp.core.agent import Agent, AgentBuilder
from langcomp.core.state import SmartState
from langcomp.swarm.pool import SwarmPool, SubAgent
from langcomp.memory.buffer import ContextBuffer, AutoSummarizer
from langcomp.tools.guard import ToolGuard, ApprovalGate
from langcomp.devtools.visualizer import GraphVisualizer, DryRunner

__all__ = [
    "Agent",
    "AgentBuilder",
    "SmartState",
    "SwarmPool",
    "SubAgent",
    "ContextBuffer",
    "AutoSummarizer",
    "ToolGuard",
    "ApprovalGate",
    "GraphVisualizer",
    "DryRunner",
]
