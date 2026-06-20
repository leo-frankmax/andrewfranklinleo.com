import os
from pathlib import Path
from typing import Literal

WRITE_ROOTS = ['sites', 'docs', 'ventures.json']


class PathGuard:
    def __init__(self, write_roots: list[str] | None = None, block_traversal: bool = True):
        self.write_roots = write_roots or WRITE_ROOTS
        self.block_traversal = block_traversal

    def _normalize(self, path: str) -> str:
        return Path(path).as_posix()

    def _has_traversal(self, path: str) -> bool:
        if not self.block_traversal:
            return False
        normalized = self._normalize(path)
        if normalized.startswith('/') or ':' in normalized:
            return True
        if normalized.startswith('~'):
            return True
        if '..' in normalized:
            return True
        if '/.' in normalized or normalized.startswith('.'):
            return True
        return False

    def _in_roots(self, path: str, roots: list[str]) -> bool:
        normalized = self._normalize(path)
        for root in roots:
            normalized_root = self._normalize(root)
            if normalized == normalized_root or normalized.startswith(normalized_root + '/'):
                return True
        return False

    def is_write_allowed(self, path: str) -> bool:
        if self._has_traversal(path):
            return False
        return self._in_roots(path, self.write_roots)

    def is_read_allowed(self, path: str) -> bool:
        if self._has_traversal(path):
            return False
        normalized = self._normalize(path)
        blocked = ['.env', '.env.local', '.env.production', '.git']
        for b in blocked:
            if normalized == b or normalized.startswith(b + '/'):
                return False
        if normalized.startswith('docker/secrets/'):
            return False
        return True

    def validate(self, operation: Literal['read', 'write'], path: str) -> dict:
        normalized = self._normalize(path)
        if self._has_traversal(path):
            return {'allowed': False, 'reason': f'Path traversal detected: {normalized}'}
        if operation == 'write':
            if not self.is_write_allowed(path):
                return {'allowed': False, 'reason': f'Write not allowed to: {normalized}. Allowed roots: {", ".join(self.write_roots)}'}
        else:
            if not self.is_read_allowed(path):
                return {'allowed': False, 'reason': f'Read not allowed to: {normalized}'}
        return {'allowed': True}
