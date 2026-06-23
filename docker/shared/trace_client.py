import json
import os
import time
from typing import Any
from urllib import request


class TraceClient:
    """Best-effort trace client that never breaks primary execution."""

    def __init__(self, component: str):
        self.component = component
        self.trace_url = os.environ.get('TRACEBOX_URL', 'http://tracebox:8088').rstrip('/')
        self.enabled = os.environ.get('TRACEBOX_ENABLED', 'true').lower() in {'1', 'true', 'yes'}
        self.run_id = os.environ.get('TRACE_RUN_ID', '').strip()
        self.timeout = float(os.environ.get('TRACEBOX_TIMEOUT_SECONDS', '1.5'))

    def emit(self, event_type: str, payload: dict[str, Any]) -> None:
        if not self.enabled:
            return

        payload_with_run = dict(payload)
        if self.run_id and not payload_with_run.get('run_id'):
            payload_with_run['run_id'] = self.run_id

        envelope = {
            'event_type': event_type,
            'component': self.component,
            'timestamp': time.time(),
            'payload': payload_with_run,
        }

        body = json.dumps(envelope).encode('utf-8')
        req = request.Request(
            f"{self.trace_url}/v1/events",
            data=body,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )

        try:
            with request.urlopen(req, timeout=self.timeout):
                pass
        except Exception:
            # Tracing should not block the primary workflow.
            pass
