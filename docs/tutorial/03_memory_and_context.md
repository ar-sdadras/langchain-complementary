# Chapter 03: Memory & Context Engine

In this chapter, you will learn how to prevent conversation history overflow errors using `ContextBuffer` and `AutoSummarizer`.

---

## ⚠️ The Context Limit Challenge

Long-running agent chats accumulate dozens of messages over time. If unmanaged, this causes LLM API token limit errors (`context_length_exceeded`).

`langcomp` provides two zero-boilerplate middleware classes:
1. `ContextBuffer`: Sliding window message trimming.
2. `AutoSummarizer`: Background conversation history summarization.

---

## ✂️ 1. Sliding Window Trimming with `ContextBuffer`

`ContextBuffer` trims conversation history to a specified maximum number of messages, while optionally preserving the initial `SystemMessage` system prompt.

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langcomp import ContextBuffer

# Create message history
messages = [
    SystemMessage(content="You are a helpful customer support agent."),
    HumanMessage(content="Hello"),
    AIMessage(content="Hi there! How can I help?"),
    HumanMessage(content="I have an issue with order #123"),
    AIMessage(content="Let me look that up for you."),
    HumanMessage(content="Is it shipped yet?"),
    AIMessage(content="Yes, it shipped yesterday."),
]

# Keep at most 4 messages while preserving system prompt
buffer = ContextBuffer(max_messages=4, preserve_system_prompt=True)
trimmed_messages = buffer.trim(messages)

print(f"Original message count: {len(messages)}")
print(f"Trimmed message count: {len(trimmed_messages)}")
for msg in trimmed_messages:
    print(f"- [{msg.__class__.__name__}]: {msg.content}")
```

> [!NOTE]
> `ContextBuffer` preserves index `0` if it is a `SystemMessage`, ensuring system instructions are never discarded during trimming.

---

## 📝 2. Background Compression with `AutoSummarizer`

Instead of simply deleting older messages, `AutoSummarizer` compresses older messages into a single summary `SystemMessage` once the conversation exceeds a trigger threshold.

```python
from langchain_core.messages import HumanMessage, AIMessage
from langcomp import AutoSummarizer

# Simulate a long conversation (20 turns)
history = []
for i in range(1, 11):
    history.append(HumanMessage(content=f"User question {i}"))
    history.append(AIMessage(content=f"Assistant answer {i}"))

# Summarize when messages exceed 10, keeping the 4 most recent messages
summarizer = AutoSummarizer(trigger_threshold=10, keep_recent=4)
compact_history = summarizer.summarize_messages(history)

print(f"Original turns: {len(history)}")
print(f"Compact turns: {len(compact_history)}")
print("\nFirst message in compact history:")
print(compact_history[0].content)
```

### Custom Summarizer Callback

You can supply a custom LLM summarization function to `summarize_messages`:

```python
def my_llm_summarizer(raw_transcript: str) -> str:
    # Call your LLM model to generate a concise summary
    return f"Key topics discussed: User asked 10 questions regarding support."

compact_history = summarizer.summarize_messages(history, summarizer_func=my_llm_summarizer)
```

---

## 📌 Memory Strategy Summary

| Feature | Primary Purpose | When to Use |
| :--- | :--- | :--- |
| `ContextBuffer` | Hard message cap | Fast API response times, rigid token limits |
| `AutoSummarizer` | Context compression | Long-running multi-turn agent conversations |
