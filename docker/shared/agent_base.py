import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Callable

from .trace_client import TraceClient


class AgentBase:
    """Base class for all CMS agents with built-in guardrails."""

    def __init__(self, agent_name: str, data_root: str = '/data'):
        self.agent_name = agent_name
        self.data_root = Path(data_root)
        env_run_id = os.environ.get('TRACE_RUN_ID', '').strip()
        self.run_id = env_run_id or str(uuid.uuid4())
        self.start_time = time.time()
        self.max_iterations = 500
        self.timeout_ms = 1800000  # 30 min
        self.iteration_count = 0
        self.errors: list[dict] = []
        self.tool_log: list[dict] = []
        self.trace = TraceClient(component=f'agent:{self.agent_name}')
        self._trace_emit('agent_run_started', {
            'agent': self.agent_name,
            'run_id': self.run_id,
            'data_root': str(self.data_root),
        })

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

    def _trace_emit(self, event_type: str, payload: dict[str, Any]) -> None:
        try:
            self.trace.emit(event_type, payload)
        except Exception:
            # Tracing is best-effort and must never break agent execution.
            pass

    def log_tool(self, tool_name: str, args: dict, result: Any, allowed: bool = True):
        self.tool_log.append({
            'tool': tool_name,
            'args': args,
            'allowed': allowed,
            'timestamp': time.time(),
            'run_id': self.run_id,
        })
        self._trace_emit('agent_tool_invocation', {
            'agent': self.agent_name,
            'run_id': self.run_id,
            'tool': tool_name,
            'allowed': allowed,
            'args': args,
            'result_type': type(result).__name__,
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

        self._trace_emit('agent_failure', {
            'agent': self.agent_name,
            'run_id': self.run_id,
            'error': str(error),
            'context': context,
            'error_file': str(error_file),
        })

    def get_elapsed_ms(self) -> float:
        return (time.time() - self.start_time) * 1000

    def emit_success(self, summary: dict | None = None) -> None:
        self._trace_emit('agent_run_completed', {
            'agent': self.agent_name,
            'run_id': self.run_id,
            'elapsed_ms': self.get_elapsed_ms(),
            'iterations': self.iteration_count,
            'summary': summary or {},
        })

    def run(self) -> dict:
        """Override in subclasses. Return result dict."""
        raise NotImplementedError
