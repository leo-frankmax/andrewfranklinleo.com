#!/usr/bin/env python3
import json
import time
import uuid
import sys
from urllib import request


TRACEBOX_URL = 'http://localhost:8088'
REQUIRED_STORES = ['postgres', 'mongo', 'redis', 'neo4j', 'chroma']
MAX_ATTEMPTS = 5


def _request_json(url: str, method: str = 'GET', body: dict | None = None) -> tuple[int, dict | None, str | None]:
    req_body = None
    headers = {}
    if body is not None:
        req_body = json.dumps(body).encode('utf-8')
        headers['Content-Type'] = 'application/json'

    req = request.Request(url, data=req_body, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=4.0) as resp:
            payload = resp.read().decode('utf-8').strip()
            parsed = json.loads(payload) if payload else {}
            return resp.status, parsed, None
    except Exception as exc:
        return 0, None, str(exc)


def check_tracebox_health() -> tuple[bool, str]:
    status, payload, err = _request_json(f'{TRACEBOX_URL}/health')
    if err:
        return False, err
    if status != 200:
        return False, f'health status={status}'
    if not isinstance(payload, dict) or payload.get('status') != 'ok':
        return False, 'health payload missing status=ok'
    return True, ''


def check_store_fanout() -> tuple[bool, dict[str, int], str]:
    run_id = f'preflight-{uuid.uuid4()}'
    event = {
        'schema_version': 'v1',
        'event_type': 'trace_preflight',
        'component': 'trace-preflight-hook',
        'payload': {
            'run_id': run_id,
            'probe': 'store-readiness',
            'timestamp': time.time(),
        },
    }

    status, _, err = _request_json(f'{TRACEBOX_URL}/v1/events', method='POST', body=event)
    if err:
        return False, {}, err
    if status != 200:
        return False, {}, f'event ingest status={status}'

    status, payload, err = _request_json(f'{TRACEBOX_URL}/v1/fanout/by-run/{run_id}')
    if err:
        return False, {}, err
    if status != 200 or not isinstance(payload, dict):
        return False, {}, f'fanout query status={status}'

    counts = payload.get('counts', {}) if isinstance(payload, dict) else {}
    if not isinstance(counts, dict):
        return False, {}, 'fanout payload missing counts'

    missing = [store for store in REQUIRED_STORES if int(counts.get(store, 0)) < 1]
    if missing:
        return False, {k: int(counts.get(k, 0)) for k in REQUIRED_STORES}, f"missing fanout for stores: {', '.join(missing)}"

    return True, {k: int(counts.get(k, 0)) for k in REQUIRED_STORES}, ''


def main() -> int:
    report: dict[str, object] = {'checks': []}
    ok = False

    for attempt in range(1, MAX_ATTEMPTS + 1):
        health_ok, health_err = check_tracebox_health()
        check = {
            'attempt': attempt,
            'name': 'tracebox-health',
            'ok': health_ok,
            'error': health_err,
        }
        cast_checks = report['checks']
        if isinstance(cast_checks, list):
            cast_checks.append(check)

        if not health_ok:
            time.sleep(2)
            continue

        fanout_ok, counts, fanout_err = check_store_fanout()
        check = {
            'attempt': attempt,
            'name': 'store-fanout',
            'ok': fanout_ok,
            'counts': counts,
            'error': fanout_err,
        }
        cast_checks = report['checks']
        if isinstance(cast_checks, list):
            cast_checks.append(check)

        if fanout_ok:
            ok = True
            break

        time.sleep(2)

    print(json.dumps(report, indent=2))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
