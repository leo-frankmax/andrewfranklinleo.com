import pytest
import sys
import json
import tempfile
import shutil
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('agent', str(Path(__file__).parent.parent / 'agent.py'))
agent_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_mod)
ContentWriter = agent_mod.ContentWriter


SAMPLE_DATA = {
    'groups': [{'id': 'frankmax', 'name': 'Frankmax', 'parentId': 'leo-global-holdings'}],
    'ventures': [
        {'id': 'frankmax-talent', 'name': 'Frankmax Talent', 'parentId': 'frankmax',
         'offerings': [{'id': 'executive-search', 'name': 'Executive Search', 'parentId': 'frankmax-talent'}]},
    ],
}


class TestContentWriter:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.agent = ContentWriter(data_root=self.tmpdir)
        # Create pre-existing site structure
        base = Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'frankmax' / 'frankmax-talent' / 'executive-search'
        base.mkdir(parents=True)
        (base / 'index.html').write_text('<h1>Placeholder</h1>')
        venture_dir = base.parent
        (venture_dir / 'index.html').write_text('<h1>Venture Placeholder</h1>')

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_enriches_pages(self):
        result = self.agent.run(SAMPLE_DATA)
        assert result['success'] is True
        assert result['pages_enriched'] >= 1

    def test_generates_seo(self):
        result = self.agent.run(SAMPLE_DATA)
        assert result['seo_generated'] >= 1

    def test_enriched_page_has_content(self):
        self.agent.run(SAMPLE_DATA)
        page = Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'frankmax' / 'frankmax-talent' / 'executive-search' / 'index.html'
        content = page.read_text()
        assert 'Executive Search' in content
        assert 'Key Benefits' in content

    def test_seo_file_created(self):
        self.agent.run(SAMPLE_DATA)
        seo_file = Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'frankmax' / 'frankmax-talent' / 'executive-search' / '_seo.json'
        assert seo_file.exists()
        seo = json.loads(seo_file.read_text())
        assert 'title' in seo

    def test_iterations_tracked(self):
        self.agent.run(SAMPLE_DATA)
        assert self.agent.iteration_count > 0
