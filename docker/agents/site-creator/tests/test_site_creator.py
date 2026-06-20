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
SiteCreator = agent_mod.SiteCreator


SAMPLE_DATA = {
    'conglomerate': {'id': 'leo-global-holdings', 'name': 'Leo Global Holdings', 'mission': 'Test'},
    'groups': [
        {'id': 'frankmax', 'name': 'Frankmax', 'type': 'group', 'parentId': 'leo-global-holdings', 'mission': 'Empowering'},
    ],
    'ventures': [
        {'id': 'frankmax-talent', 'name': 'Frankmax Talent', 'parentId': 'frankmax', 'mission': 'Recruit',
         'offerings': [{'id': 'executive-search', 'name': 'Executive Search', 'parentId': 'frankmax-talent'}]},
    ],
}


class TestSiteCreator:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.agent = SiteCreator(data_root=self.tmpdir)

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_creates_directories(self):
        result = self.agent.run(SAMPLE_DATA.copy())
        assert result['success'] is True
        assert result['directories_created'] >= 3

    def test_creates_pages(self):
        result = self.agent.run(SAMPLE_DATA.copy())
        assert result['pages_created'] >= 3

    def test_creates_metadata(self):
        result = self.agent.run(SAMPLE_DATA.copy())
        assert result['metadata_created'] >= 3

    def test_creates_conglomerate_portal(self):
        self.agent.run(SAMPLE_DATA.copy())
        portal = Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'index.html'
        assert portal.exists()
        content = portal.read_text()
        assert 'Leo Global Holdings' in content

    def test_creates_group_page(self):
        self.agent.run(SAMPLE_DATA.copy())
        group_page = Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'frankmax' / 'index.html'
        assert group_page.exists()
        assert 'Frankmax' in group_page.read_text()

    def test_creates_venture_page(self):
        self.agent.run(SAMPLE_DATA.copy())
        venture_page = Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'frankmax' / 'frankmax-talent' / 'index.html'
        assert venture_page.exists()
        assert 'Frankmax Talent' in venture_page.read_text()

    def test_creates_offering_page(self):
        self.agent.run(SAMPLE_DATA.copy())
        offering_page = Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'frankmax' / 'frankmax-talent' / 'executive-search' / 'index.html'
        assert offering_page.exists()

    def test_creates_metadata_files(self):
        self.agent.run(SAMPLE_DATA.copy())
        group_meta = Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'frankmax' / '_group.json'
        assert group_meta.exists()
        data = json.loads(group_meta.read_text())
        assert data['name'] == 'Frankmax'

    def test_creates_breadcrumbs(self):
        self.agent.run(SAMPLE_DATA.copy())
        venture_page = Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'frankmax' / 'frankmax-talent' / 'index.html'
        content = venture_page.read_text()
        assert 'breadcrumb' in content
        assert 'Home' in content

    def test_iterations_tracked(self):
        self.agent.run(SAMPLE_DATA.copy())
        assert self.agent.iteration_count > 0
