import json
import time
import uuid
from pathlib import Path
from typing import Any, Callable


class AgentBase:
    """Base class for all CMS agents with built-in guardrails."""

    def __init__(self, agent_name: str, data_root: str = '/data'):
        self.agent_name = agent_name
        self.data_root = Path(data_root)
        self.run_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.max_iterations = 500
        self.timeout_ms = 1800000  # 30 min
        self.iteration_count = 0
        self.errors: list[dict] = []
        self.tool_log: list[dict] = []

    def should_stop(self) -> bool:
        if self.iteration_count >= self.max_iterations:
            return True
        elapsed = (time.time() - self.start_time) * 1000
        if elapsed >= self.timeout_ms:
            return True
        return False

    def get_stop_reason(self) -> str | None:
        if self.iteration_count >= self.max_iterations:
            return f"Agent '{self.agent_name}' reached max iterations ({self.max_iterations})"
        elapsed = (time.time() - self.start_time) * 1000
        if elapsed >= self.timeout_ms:
            return f"Agent '{self.agent_name}' timeout after {self.timeout_ms}ms"
        return None

    def increment(self):
        self.iteration_count += 1

    def log_tool(self, tool_name: str, args: dict, result: Any, allowed: bool = True):
        self.tool_log.append({
            'tool': tool_name,
            'args': args,
            'allowed': allowed,
            'timestamp': time.time(),
            'run_id': self.run_id,
        })

    def emit_failure(self, error: Exception, context: dict) -> None:
        artifact = {
            'agent': self.agent_name,
            'error': str(error),
            'stack': getattr(error, '__traceback__', None).__class__.__name__ if hasattr(error, '__traceback__') else None,
            'timestamp': time.time(),
            'run_id': self.run_id,
            'context': context,
        }
        error_file = self.data_root / f'{self.agent_name}.error.json'
        try:
            error_file.parent.mkdir(parents=True, exist_ok=True)
            error_file.write_text(json.dumps(artifact, indent=2))
        except Exception:
            pass

    def get_elapsed_ms(self) -> float:
        return (time.time() - self.start_time) * 1000

    def run(self) -> dict:
        """Override in subclasses. Return result dict."""
        raise NotImplementedError
