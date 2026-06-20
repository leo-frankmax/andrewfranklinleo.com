import pytest
import os
import tempfile
import json
from pathlib import Path

from shared.path_guard import PathGuard


class TestFsMcpTools:
    """Test fs-mcp tool implementations (without MCP protocol)."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.guard = PathGuard()
        # Create test structure
        os.makedirs(os.path.join(self.tmpdir, 'sites', 'test-group', 'test-venture'), exist_ok=True)
        with open(os.path.join(self.tmpdir, 'sites', 'test.html'), 'w') as f:
            f.write('<h1>Test</h1>')
        with open(os.path.join(self.tmpdir, 'sites', 'data.json'), 'w') as f:
            json.dump({'key': 'value'}, f)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _resolve(self, path: str) -> str:
        return os.path.join(self.tmpdir, path)

    def test_read_file(self):
        path = self._resolve('sites/test.html')
        with open(path) as f:
            content = f.read()
        assert content == '<h1>Test</h1>'

    def test_write_file(self):
        path = self._resolve('sites/new.html')
        with open(path, 'w') as f:
            f.write('<p>New</p>')
        assert os.path.exists(path)
        with open(path) as f:
            assert f.read() == '<p>New</p>'

    def test_write_file_blocked_by_guard(self):
        assert self.guard.is_write_allowed('package.json') is False

    def test_create_directory(self):
        path = self._resolve('sites/new-dir/subdir')
        os.makedirs(path, exist_ok=True)
        assert os.path.isdir(path)

    def test_list_directory(self):
        path = self._resolve('sites')
        entries = os.listdir(path)
        assert 'test.html' in entries
        assert 'data.json' in entries
        assert 'test-group' in entries

    def test_read_json(self):
        path = self._resolve('sites/data.json')
        with open(path) as f:
            data = json.load(f)
        assert data == {'key': 'value'}

    def test_write_json(self):
        path = self._resolve('sites/output.json')
        with open(path, 'w') as f:
            json.dump({'output': True}, f, indent=2)
        with open(path) as f:
            data = json.load(f)
        assert data == {'output': True}

    def test_file_exists(self):
        assert os.path.exists(self._resolve('sites/test.html')) is True
        assert os.path.exists(self._resolve('sites/nonexistent.html')) is False

    def test_get_file_size(self):
        path = self._resolve('sites/test.html')
        size = os.path.getsize(path)
        assert size > 0

    def test_delete_file(self):
        path = self._resolve('sites/to-delete.html')
        with open(path, 'w') as f:
            f.write('delete me')
        assert os.path.exists(path)
        os.remove(path)
        assert not os.path.exists(path)

    def test_move_file(self):
        src = self._resolve('sites/original.html')
        dst = self._resolve('sites/moved.html')
        with open(src, 'w') as f:
            f.write('move me')
        os.rename(src, dst)
        assert not os.path.exists(src)
        assert os.path.exists(dst)

    def test_copy_file(self):
        import shutil
        src = self._resolve('sites/copy-source.html')
        dst = self._resolve('sites/copy-dest.html')
        with open(src, 'w') as f:
            f.write('copy me')
        shutil.copy2(src, dst)
        assert os.path.exists(src)
        assert os.path.exists(dst)
        with open(dst) as f:
            assert f.read() == 'copy me'
