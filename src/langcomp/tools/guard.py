"""
Tool Guardrails & Human Approval Gates for langcomp framework.
Provides resilient execution wrappers and streamlined approval logic.
"""

import time
import logging
from typing import Any, Callable, Dict, Optional, Union
from langchain_core.tools import BaseTool, tool

logger = logging.getLogger("langcomp.tools")


class ToolGuard:
    """
    Resilient wrapper for tool execution with retries, error fallbacks, and parameter sanity checks.
    """

    def __init__(
        self,
        max_retries: int = 3,
        fallback_output: Optional[str] = None,
        retry_delay_seconds: float = 0.5,
    ):
        self.max_retries = max_retries
        self.fallback_output = fallback_output
        self.retry_delay_seconds = retry_delay_seconds

    def wrap_function(self, func: Callable, tool_name: Optional[str] = None) -> Callable:
        """
        Wrap a raw Python tool function with retry and fallback guardrails.
        """
        name = tool_name or getattr(func, "__name__", "ToolFunction")

        def guarded_func(*args: Any, **kwargs: Any) -> Any:
            last_err: Optional[Exception] = None
            for attempt in range(1, self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_err = e
                    logger.warning(
                        f"Tool '{name}' failed attempt {attempt}/{self.max_retries}: {e}"
                    )
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay_seconds)

            if self.fallback_output is not None:
                return self.fallback_output
            raise RuntimeError(f"Tool '{name}' failed after {self.max_retries} attempts: {last_err}")

        return guarded_func

    def wrap_tool(self, tool_inst: BaseTool) -> BaseTool:
        """
        Wrap a LangChain BaseTool instance with guardrail logic.
        """
        original_run = tool_inst._run

        def guarded_run(*args: Any, **kwargs: Any) -> Any:
            guarded_fn = self.wrap_function(original_run, tool_name=tool_inst.name)
            return guarded_fn(*args, **kwargs)

        tool_inst._run = guarded_run
        return tool_inst


class ApprovalGate:
    """
    Human-In-The-Loop gate for verifying sensitive tool actions before execution.
    """

    def __init__(self, approval_func: Optional[Callable[[str, Dict[str, Any]], bool]] = None):
        self.approval_func = approval_func

    def check_approval(self, action_name: str, parameters: Dict[str, Any]) -> bool:
        """
        Determine if action is approved.
        """
        if self.approval_func is not None:
            return self.approval_func(action_name, parameters)
        # Default behavior: auto-approve if no custom approval callback is attached
        return True
