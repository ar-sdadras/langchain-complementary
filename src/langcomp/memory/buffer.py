"""
Memory & Context Management for langcomp framework.
Provides sliding window message trimming and automatic context summarization.
"""

from typing import Any, Dict, List, Optional
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage


class ContextBuffer:
    """
    Sliding window message buffer that trims conversation history to prevent context overflow.
    """

    def __init__(self, max_messages: int = 10, preserve_system_prompt: bool = True):
        self.max_messages = max_messages
        self.preserve_system_prompt = preserve_system_prompt

    def trim(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        Trim messages to at most max_messages while preserving optional system prompt at index 0.
        """
        if not messages or len(messages) <= self.max_messages:
            return messages

        system_msg: Optional[BaseMessage] = None
        if self.preserve_system_prompt and isinstance(messages[0], SystemMessage):
            system_msg = messages[0]
            remaining = messages[1:]
        else:
            remaining = messages

        # Keep the last max_messages
        keep_count = self.max_messages - (1 if system_msg else 0)
        trimmed_tail = remaining[-keep_count:] if keep_count > 0 else []

        if system_msg:
            return [system_msg] + trimmed_tail
        return trimmed_tail


class AutoSummarizer:
    """
    Automatically compresses older conversation history into a single summary SystemMessage.
    """

    def __init__(self, trigger_threshold: int = 15, keep_recent: int = 5):
        self.trigger_threshold = trigger_threshold
        self.keep_recent = keep_recent

    def summarize_messages(
        self,
        messages: List[BaseMessage],
        summarizer_func: Optional[Any] = None,
    ) -> List[BaseMessage]:
        """
        If messages exceed trigger_threshold, summarize older messages.
        """
        if len(messages) <= self.trigger_threshold:
            return messages

        system_msg: Optional[BaseMessage] = None
        if isinstance(messages[0], SystemMessage):
            system_msg = messages[0]
            work_messages = messages[1:]
        else:
            work_messages = messages

        old_messages = work_messages[:-self.keep_recent]
        recent_messages = work_messages[-self.keep_recent:]

        if not old_messages:
            return messages

        # Combine text content of old messages
        lines = []
        for m in old_messages:
            role = m.__class__.__name__.replace("Message", "")
            lines.append(f"{role}: {m.content}")
        summary_text = "\n".join(lines)

        if summarizer_func is not None:
            try:
                computed_summary = summarizer_func(summary_text)
                summary_content = f"Previous Conversation Summary:\n{computed_summary}"
            except Exception:
                summary_content = f"Previous Conversation Summary:\n{summary_text[:500]}..."
        else:
            summary_content = f"Previous Conversation Summary:\n{summary_text[:500]}..."

        summary_system_msg = SystemMessage(content=summary_content)

        result: List[BaseMessage] = []
        if system_msg:
            result.append(system_msg)
        result.append(summary_system_msg)
        result.extend(recent_messages)

        return result
