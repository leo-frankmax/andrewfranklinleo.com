import pytest
import tempfile
import json
import os
from pathlib import Path

from server import RegistryMcpServer


class TestRegistryMcp:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.registry_path = os.path.join(self.tmpdir, 'registry.json')
        self.server = RegistryMcpServer(self.registry_path)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_register_plugin(self):
        result = self.server.register_plugin('seo-enhancer', {
            'version': '1.0.0',
            'hooks': ['post-generate'],
        })
        assert result['success'] is True
        assert result['name'] == 'seo-enhancer'

    def test_list_plugins(self):
        self.server.register_plugin('test-plugin', {'version': '1.0.0'})
        result = self.server.list_plugins()
        assert 'test-plugin' in result['plugins']

    def test_get_plugin(self):
        self.server.register_plugin('my-plugin', {'version': '2.0.0', 'config': {'key': 'val'}})
        plugin = self.server.get_plugin('my-plugin')
        assert plugin is not None
        assert plugin['version'] == '2.0.0'

    def test_register_skill(self):
        result = self.server.register_skill('venture-lister', {
            'mcp_servers': ['content-mcp', 'graph-mcp'],
        })
        assert result['success'] is True

    def test_list_skills(self):
        self.server.register_skill('test-skill', {})
        result = self.server.list_skills()
        assert 'test-skill' in result['skills']

    def test_get_skill(self):
        self.server.register_skill('my-skill', {'description': 'Test skill'})
        skill = self.server.get_skill('my-skill')
        assert skill['description'] == 'Test skill'

    def test_register_hook(self):
        result = self.server.register_hook('post-build', {
            'event': 'build.complete',
            'handler': 'deploy-handler',
            'priority': 10,
        })
        assert result['success'] is True

    def test_list_hooks(self):
        self.server.register_hook('test-hook', {'event': 'test'})
        result = self.server.list_hooks()
        assert 'test-hook' in result['hooks']

    def test_resolve_dependencies(self):
        self.server.register_plugin('a', {'dependencies': ['b']})
        self.server.register_plugin('b', {'version': '1.2.0'})
        result = self.server.resolve_dependencies('a')
        assert len(result['dependencies']) == 1
        assert result['dependencies'][0]['name'] == 'b'

    def test_resolve_dependencies_missing(self):
        self.server.register_plugin('a', {'dependencies': ['missing']})
        result = self.server.resolve_dependencies('a')
        assert result['dependencies'][0].get('error') == 'not found'

    def test_get_plugin_config(self):
        self.server.register_plugin('cfg-plugin', {'config': {'api_key': 'xyz'}})
        config = self.server.get_plugin_config('cfg-plugin')
        assert config['api_key'] == 'xyz'

    def test_update_plugin_config(self):
        self.server.register_plugin('cfg-plugin', {'config': {'key': 'old'}})
        self.server.update_plugin_config('cfg-plugin', {'key': 'new'})
        config = self.server.get_plugin_config('cfg-plugin')
        assert config['key'] == 'new'

    def test_persistence(self):
        self.server.register_plugin('persist', {'version': '1.0.0'})
        server2 = RegistryMcpServer(self.registry_path)
        plugin = server2.get_plugin('persist')
        assert plugin is not None
