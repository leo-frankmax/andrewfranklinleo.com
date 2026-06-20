import pytest
import os
import tempfile
import json
from pathlib import Path

from shared.path_guard import PathGuard


class TestPathGuard:
    def setup_method(self):
        self.guard = PathGuard()

    def test_allows_write_to_sites(self):
        assert self.guard.is_write_allowed('sites/leo-global-holdings/frankmax/index.html') is True

    def test_allows_write_to_docs(self):
        assert self.guard.is_write_allowed('docs/index.html') is True

    def test_allows_write_to_ventures_json(self):
        assert self.guard.is_write_allowed('ventures.json') is True

    def test_blocks_write_to_memory(self):
        assert self.guard.is_write_allowed('memory/secret.md') is False

    def test_blocks_write_to_github(self):
        assert self.guard.is_write_allowed('.github/workflows/test.yml') is False

    def test_blocks_write_to_docker(self):
        assert self.guard.is_write_allowed('docker/compose.yml') is False

    def test_blocks_write_to_src(self):
        assert self.guard.is_write_allowed('src/guards/test.ts') is False

    def test_blocks_write_to_package_json(self):
        assert self.guard.is_write_allowed('package.json') is False

    def test_blocks_traversal_dotdot(self):
        assert self.guard.is_write_allowed('sites/../package.json') is False

    def test_blocks_absolute_path(self):
        assert self.guard.is_write_allowed('/etc/passwd') is False

    def test_blocks_windows_absolute(self):
        assert self.guard.is_write_allowed('C:\\Windows\\System32') is False

    def test_blocks_tilde(self):
        assert self.guard.is_write_allowed('~/.ssh/id_rsa') is False

    def test_allows_read_from_sites(self):
        assert self.guard.is_read_allowed('sites/test.html') is True

    def test_allows_read_from_memory(self):
        assert self.guard.is_read_allowed('memory/test.md') is True

    def test_blocks_read_dotenv(self):
        assert self.guard.is_read_allowed('.env') is False

    def test_blocks_read_git(self):
        assert self.guard.is_read_allowed('.git/config') is False

    def test_blocks_read_docker_secrets(self):
        assert self.guard.is_read_allowed('docker/secrets/key.txt') is False

    def test_validate_write_success(self):
        result = self.guard.validate('write', 'sites/test.html')
        assert result['allowed'] is True

    def test_validate_write_failure(self):
        result = self.guard.validate('write', '../escape')
        assert result['allowed'] is False
        assert 'traversal' in result['reason']

    def test_validate_read_success(self):
        result = self.guard.validate('read', 'memory/test.md')
        assert result['allowed'] is True

    def test_validate_read_failure(self):
        result = self.guard.validate('read', '.env')
        assert result['allowed'] is False
