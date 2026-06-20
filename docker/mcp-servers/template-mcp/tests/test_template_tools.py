import pytest
import tempfile
import os
from pathlib import Path

from server import TemplateMcpServer


class TestTemplateMcp:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmpdir, 'templates'), exist_ok=True)
        with open(os.path.join(self.tmpdir, 'templates', 'test.html'), 'w') as f:
            f.write('<h1>{{title}}</h1><p>{{description}}</p>')
        self.server = TemplateMcpServer(
            templates_dir=os.path.join(self.tmpdir, 'templates')
        )

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_render_template(self):
        result = self.server.render_template('test.html', {
            'title': 'Hello',
            'description': 'World',
        })
        assert 'Hello' in result['html']
        assert 'World' in result['html']

    def test_get_template(self):
        result = self.server.get_template('test.html')
        assert '{{title}}' in result['content']

    def test_list_templates(self):
        result = self.server.list_templates()
        assert len(result['templates']) == 1
        assert result['templates'][0]['name'] == 'test.html'

    def test_apply_global_layout(self):
        result = self.server.apply_global_layout('<p>Content</p>', 'Test Page')
        assert '<p>Content</p>' in result['html']
        assert 'Test Page' in result['html']
        assert '<!DOCTYPE html>' in result['html']

    def test_render_breadcrumb(self):
        result = self.server.render_breadcrumb([
            {'label': 'Home', 'url': '/'},
            {'label': 'Test', 'url': '/test/'},
        ])
        assert 'Home' in result['html']
        assert 'Test' in result['html']
        assert 'aria-current="page"' in result['html']

    def test_render_card(self):
        result = self.server.render_card({
            'title': 'Card Title',
            'description': 'Card Desc',
            'url': '/test/',
            'icon': 'star',
        })
        assert 'Card Title' in result['html']
        assert 'Card Desc' in result['html']

    def test_validate_html_safe(self):
        result = self.server.validate_html('<p>Hello</p>')
        assert result['valid'] is True

    def test_validate_html_script(self):
        result = self.server.validate_html('<script>alert(1)</script>')
        assert result['valid'] is False
        assert 'Script tags' in result['issues'][0]

    def test_validate_html_event_handler(self):
        result = self.server.validate_html('<img onerror="alert(1)">')
        assert result['valid'] is False
        assert 'Event handlers' in result['issues'][0]

    def test_interpolate_strips_missing(self):
        result = self.server.render_template('test.html', {})
        assert '{{' not in result['html']
