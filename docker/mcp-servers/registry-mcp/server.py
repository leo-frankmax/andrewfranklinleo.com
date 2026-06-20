import json
from pathlib import Path
from typing import Any


class RegistryMcpServer:
    def __init__(self, registry_path: str = '/data/registry.json'):
        self.registry_path = Path(registry_path)
        self._registry = self._load_registry()

    def _load_registry(self) -> dict:
        if self.registry_path.exists():
            return json.loads(self.registry_path.read_text())
        return {'plugins': {}, 'skills': {}, 'hooks': {}}

    def _save_registry(self):
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(json.dumps(self._registry, indent=2))

    def list_plugins(self) -> dict:
        return {'plugins': list(self._registry.get('plugins', {}).keys())}

    def get_plugin(self, name: str) -> dict | None:
        return self._registry.get('plugins', {}).get(name)

    def register_plugin(self, name: str, config: dict) -> dict:
        if 'plugins' not in self._registry:
            self._registry['plugins'] = {}
        self._registry['plugins'][name] = {
            'version': config.get('version', '0.1.0'),
            'enabled': config.get('enabled', True),
            'dependencies': config.get('dependencies', []),
            'hooks': config.get('hooks', []),
            'config': config.get('config', {}),
        }
        self._save_registry()
        return {'success': True, 'name': name}

    def list_skills(self) -> dict:
        return {'skills': list(self._registry.get('skills', {}).keys())}

    def get_skill(self, name: str) -> dict | None:
        return self._registry.get('skills', {}).get(name)

    def register_skill(self, name: str, config: dict) -> dict:
        if 'skills' not in self._registry:
            self._registry['skills'] = {}
        self._registry['skills'][name] = {
            'version': config.get('version', '0.1.0'),
            'mcp_servers': config.get('mcp_servers', []),
            'description': config.get('description', ''),
        }
        self._save_registry()
        return {'success': True, 'name': name}

    def list_hooks(self) -> dict:
        return {'hooks': list(self._registry.get('hooks', {}).keys())}

    def register_hook(self, name: str, config: dict) -> dict:
        if 'hooks' not in self._registry:
            self._registry['hooks'] = {}
        self._registry['hooks'][name] = {
            'event': config.get('event', ''),
            'handler': config.get('handler', ''),
            'priority': config.get('priority', 0),
        }
        self._save_registry()
        return {'success': True, 'name': name}

    def resolve_dependencies(self, name: str) -> dict:
        plugin = self._registry.get('plugins', {}).get(name)
        if not plugin:
            return {'error': f'Plugin not found: {name}'}
        deps = plugin.get('dependencies', [])
        resolved = []
        for dep in deps:
            dep_plugin = self._registry.get('plugins', {}).get(dep)
            if dep_plugin:
                resolved.append({'name': dep, 'version': dep_plugin.get('version', '0.1.0')})
            else:
                resolved.append({'name': dep, 'error': 'not found'})
        return {'plugin': name, 'dependencies': resolved}

    def get_plugin_config(self, name: str) -> dict:
        plugin = self._registry.get('plugins', {}).get(name)
        if not plugin:
            return {'error': f'Plugin not found: {name}'}
        return plugin.get('config', {})

    def update_plugin_config(self, name: str, config: dict) -> dict:
        plugin = self._registry.get('plugins', {}).get(name)
        if not plugin:
            return {'error': f'Plugin not found: {name}'}
        plugin['config'].update(config)
        self._save_registry()
        return {'success': True, 'name': name}


TOOLS = {
    'list_plugins': {'description': 'List available plugins', 'inputSchema': {'type': 'object', 'properties': {}}},
    'get_plugin': {'description': 'Get plugin details', 'inputSchema': {'type': 'object', 'properties': {'name': {'type': 'string'}}, 'required': ['name']}},
    'register_plugin': {'description': 'Register new plugin', 'inputSchema': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'config': {'type': 'object'}}, 'required': ['name', 'config']}},
    'list_skills': {'description': 'List available skills', 'inputSchema': {'type': 'object', 'properties': {}}},
    'get_skill': {'description': 'Get skill details', 'inputSchema': {'type': 'object', 'properties': {'name': {'type': 'string'}}, 'required': ['name']}},
    'register_skill': {'description': 'Register new skill', 'inputSchema': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'config': {'type': 'object'}}, 'required': ['name', 'config']}},
    'list_hooks': {'description': 'List available hooks', 'inputSchema': {'type': 'object', 'properties': {}}},
    'register_hook': {'description': 'Register new hook', 'inputSchema': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'config': {'type': 'object'}}, 'required': ['name', 'config']}},
    'resolve_dependencies': {'description': 'Get dependency tree', 'inputSchema': {'type': 'object', 'properties': {'name': {'type': 'string'}}, 'required': ['name']}},
    'get_plugin_config': {'description': 'Get plugin configuration', 'inputSchema': {'type': 'object', 'properties': {'name': {'type': 'string'}}, 'required': ['name']}},
    'update_plugin_config': {'description': 'Update plugin config', 'inputSchema': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'config': {'type': 'object'}}, 'required': ['name', 'config']}},
}
