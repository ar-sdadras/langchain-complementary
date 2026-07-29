"""
Unit tests for langcomp.tools.guard.
"""

import pytest
from langcomp.tools.guard import ToolGuard, ApprovalGate


def test_tool_guard_retry_and_fallback():
    attempts = 0

    def flaky_fn(x: int) -> int:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Temporary glitch")
        return x * 2

    guard = ToolGuard(max_retries=3, retry_delay_seconds=0.01)
    guarded_fn = guard.wrap_function(flaky_fn)

    res = guarded_fn(5)
    assert res == 10
    assert attempts == 3


def test_tool_guard_fallback_output():
    def failing_fn():
        raise RuntimeError("Fatal error")

    guard = ToolGuard(max_retries=2, fallback_output="Fallback Result", retry_delay_seconds=0.01)
    guarded_fn = guard.wrap_function(failing_fn)

    res = guarded_fn()
    assert res == "Fallback Result"


def test_approval_gate():
    gate = ApprovalGate(approval_func=lambda action, params: params.get("safe", False))

    assert gate.check_approval("delete_db", {"safe": False}) is False
    assert gate.check_approval("read_data", {"safe": True}) is True
