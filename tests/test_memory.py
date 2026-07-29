"""
Unit tests for langcomp.memory.buffer.
"""

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langcomp.memory.buffer import ContextBuffer, AutoSummarizer


def test_context_buffer_trimming():
    sys_msg = SystemMessage(content="System instruction")
    messages = [sys_msg] + [HumanMessage(content=f"Msg {i}") for i in range(15)]

    buffer = ContextBuffer(max_messages=5, preserve_system_prompt=True)
    trimmed = buffer.trim(messages)

    assert len(trimmed) == 5
    assert isinstance(trimmed[0], SystemMessage)
    assert trimmed[0].content == "System instruction"
    assert trimmed[-1].content == "Msg 14"


def test_auto_summarizer():
    messages = [HumanMessage(content=f"Turn {i}") for i in range(20)]

    summarizer = AutoSummarizer(trigger_threshold=10, keep_recent=3)
    summarized = summarizer.summarize_messages(messages)

    assert len(summarized) == 4  # 1 summary SystemMessage + 3 recent
    assert isinstance(summarized[0], SystemMessage)
    assert "Previous Conversation Summary:" in summarized[0].content
    assert summarized[-1].content == "Turn 19"
