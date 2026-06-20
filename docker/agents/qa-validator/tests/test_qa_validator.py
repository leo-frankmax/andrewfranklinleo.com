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
QaValidator = agent_mod.QaValidator


SAMPLE_DATA = {
    'groups': [{'id': 'frankmax', 'name': 'Frankmax', 'parentId': 'leo-global-holdings'}],
    'ventures': [
        {'id': 'frankmax-talent', 'name': 'Frankmax Talent', 'parentId': 'frankmax',
         'offerings': [{'id': 'executive-search', 'name': 'Executive Search', 'parentId': 'frankmax-talent'}]},
    ],
}


class TestQaValidator:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.agent = QaValidator(data_root=self.tmpdir)

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _create_valid_site(self):
        base = Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'frankmax' / 'frankmax-talent' / 'executive-search'
        base.mkdir(parents=True)
        (base / 'index.html').write_text('<html><head><title>Test</title></head><body></body></html>')
        (base / '_offering.json').write_text(json.dumps({'id': 'executive-search', 'name': 'Executive Search'}))
        venture_dir = base.parent
        (venture_dir / 'index.html').write_text('<html><head><title>Venture</title></head><body></body></html>')
        (venture_dir / '_venture.json').write_text(json.dumps({'id': 'frankmax-talent', 'name': 'Frankmax Talent'}))

    def test_validates_valid_site(self):
        self._create_valid_site()
        result = self.agent.run(SAMPLE_DATA)
        assert result['success'] is True
        assert result['validation_passed'] is True
        assert result['pages_validated'] >= 2

    def test_detects_missing_pages(self):
        result = self.agent.run(SAMPLE_DATA)
        assert result['success'] is True
        assert len(result['orphan_pages']) > 0

    def test_detects_missing_metadata(self):
        self._create_valid_site()
        # Remove metadata
        (Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'frankmax' / 'frankmax-talent' / '_venture.json').unlink()
        result = self.agent.run(SAMPLE_DATA)
        assert len(result['missing_metadata']) > 0

    def test_validates_html_structure(self):
        self._create_valid_site()
        result = self.agent.run(SAMPLE_DATA)
        assert result['pages_validated'] >= 2

    def test_iterations_tracked(self):
        self._create_valid_site()
        self.agent.run(SAMPLE_DATA)
        assert self.agent.iteration_count > 0
