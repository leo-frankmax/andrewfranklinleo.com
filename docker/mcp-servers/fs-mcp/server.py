import os
import json
import shutil
from pathlib import Path
from typing import Any

# MCP server implementation using stdio
# This would normally use the `mcp` library, but we implement the core logic here
# for testing and Docker container use.

class FsMcpServer:
    def __init__(self, root_path: str = '/data'):
        self.root_path = Path(root_path)
        self.allowed_extensions = {'.html', '.json', '.css', '.js', '.md', '.xml'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB

    def _resolve(self, path: str) -> Path:
        resolved = (self.root_path / path).resolve()
        if not str(resolved).startswith(str(self.root_path.resolve())):
            raise ValueError(f'Path escapes root: {path}')
        return resolved

    def _validate_ext(self, path: Path) -> bool:
        if path.suffix and path.suffix not in self.allowed_extensions:
            return False
        return True

    def read_file(self, path: str) -> str:
        resolved = self._resolve(path)
        if not resolved.exists():
            raise FileNotFoundError(f'File not found: {path}')
        return resolved.read_text(encoding='utf-8')

    def write_file(self, path: str, content: str) -> dict:
        resolved = self._resolve(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding='utf-8')
        return {'success': True, 'path': path, 'size': len(content)}

    def create_directory(self, path: str) -> dict:
        resolved = self._resolve(path)
        resolved.mkdir(parents=True, exist_ok=True)
        return {'success': True, 'path': path}

    def list_directory(self, path: str) -> list[dict]:
        resolved = self._resolve(path)
        if not resolved.exists():
            raise FileNotFoundError(f'Directory not found: {path}')
        entries = []
        for entry in sorted(resolved.iterdir()):
            entries.append({
                'name': entry.name,
                'type': 'directory' if entry.is_dir() else 'file',
                'size': entry.stat().st_size if entry.is_file() else 0,
            })
        return entries

    def delete_file(self, path: str) -> dict:
        resolved = self._resolve(path)
        if not resolved.exists():
            raise FileNotFoundError(f'File not found: {path}')
        if resolved.is_dir():
            shutil.rmtree(resolved)
        else:
            resolved.unlink()
        return {'success': True, 'path': path}

    def read_json(self, path: str) -> Any:
        content = self.read_file(path)
        return json.loads(content)

    def write_json(self, path: str, data: Any) -> dict:
        content = json.dumps(data, indent=2, ensure_ascii=False)
        return self.write_file(path, content)

    def move_file(self, src: str, dst: str) -> dict:
        src_resolved = self._resolve(src)
        dst_resolved = self._resolve(dst)
        if not src_resolved.exists():
            raise FileNotFoundError(f'Source not found: {src}')
        dst_resolved.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_resolved), str(dst_resolved))
        return {'success': True, 'src': src, 'dst': dst}

    def copy_file(self, src: str, dst: str) -> dict:
        src_resolved = self._resolve(src)
        dst_resolved = self._resolve(dst)
        if not src_resolved.exists():
            raise FileNotFoundError(f'Source not found: {src}')
        dst_resolved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src_resolved), str(dst_resolved))
        return {'success': True, 'src': src, 'dst': dst}

    def file_exists(self, path: str) -> dict:
        resolved = self._resolve(path)
        return {'exists': resolved.exists(), 'path': path}

    def get_file_size(self, path: str) -> dict:
        resolved = self._resolve(path)
        if not resolved.exists():
            raise FileNotFoundError(f'File not found: {path}')
        return {'size': resolved.stat().st_size, 'path': path}


# Tool registry for MCP protocol
TOOLS = {
    'read_file': {
        'description': 'Read file contents from sites/',
        'inputSchema': {
            'type': 'object',
            'properties': {'path': {'type': 'string'}},
            'required': ['path'],
        },
    },
    'write_file': {
        'description': 'Write file to sites/',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'path': {'type': 'string'},
                'content': {'type': 'string'},
            },
            'required': ['path', 'content'],
        },
    },
    'create_directory': {
        'description': 'Create directory structure',
        'inputSchema': {
            'type': 'object',
            'properties': {'path': {'type': 'string'}},
            'required': ['path'],
        },
    },
    'list_directory': {
        'description': 'List contents of directory',
        'inputSchema': {
            'type': 'object',
            'properties': {'path': {'type': 'string'}},
            'required': ['path'],
        },
    },
    'delete_file': {
        'description': 'Remove file',
        'inputSchema': {
            'type': 'object',
            'properties': {'path': {'type': 'string'}},
            'required': ['path'],
        },
    },
    'read_json': {
        'description': 'Read and parse JSON metadata file',
        'inputSchema': {
            'type': 'object',
            'properties': {'path': {'type': 'string'}},
            'required': ['path'],
        },
    },
    'write_json': {
        'description': 'Write JSON metadata file',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'path': {'type': 'string'},
                'data': {'type': 'object'},
            },
            'required': ['path', 'data'],
        },
    },
    'move_file': {
        'description': 'Move/rename file',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'src': {'type': 'string'},
                'dst': {'type': 'string'},
            },
            'required': ['src', 'dst'],
        },
    },
    'copy_file': {
        'description': 'Copy file',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'src': {'type': 'string'},
                'dst': {'type': 'string'},
            },
            'required': ['src', 'dst'],
        },
    },
    'file_exists': {
        'description': 'Check if file exists',
        'inputSchema': {
            'type': 'object',
            'properties': {'path': {'type': 'string'}},
            'required': ['path'],
        },
    },
    'get_file_size': {
        'description': 'Get file size in bytes',
        'inputSchema': {
            'type': 'object',
            'properties': {'path': {'type': 'string'}},
            'required': ['path'],
        },
    },
}
