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
GraphBuilder = agent_mod.GraphBuilder


SAMPLE_DATA = {
    'groups': [{'id': 'frankmax', 'name': 'Frankmax', 'type': 'group', 'parentId': 'leo-global-holdings'}],
    'ventures': [
        {'id': 'frankmax-talent', 'name': 'Frankmax Talent', 'parentId': 'frankmax'},
        {'id': 'frankmax-learning', 'name': 'Frankmax Learning', 'parentId': 'frankmax'},
    ],
}


class TestGraphBuilder:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.agent = GraphBuilder(data_root=self.tmpdir)
        # Create pre-existing site structure
        for vid in ['frankmax-talent', 'frankmax-learning']:
            vdir = Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'frankmax' / vid
            vdir.mkdir(parents=True)
            (vdir / 'index.html').write_text(f'<html><body><main><h1>{vid}</h1></main></body></html>')
            (vdir / '_venture.json').write_text(json.dumps({'id': vid, 'name': vid}))

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_builds_global_nav(self):
        result = self.agent.run(SAMPLE_DATA)
        assert result['success'] is True
        assert result['nav_updated'] is True

    def test_nav_file_created(self):
        self.agent.run(SAMPLE_DATA)
        nav_path = Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'global-nav.json'
        assert nav_path.exists()
        nav = json.loads(nav_path.read_text())
        assert len(nav['groups']) >= 1

    def test_adds_cross_links(self):
        result = self.agent.run(SAMPLE_DATA)
        assert result['cross_links_added'] >= 1

    def test_updates_metadata(self):
        result = self.agent.run(SAMPLE_DATA)
        assert result['metadata_updated'] >= 1

    def test_metadata_has_related(self):
        self.agent.run(SAMPLE_DATA)
        meta_path = Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'frankmax' / 'frankmax-talent' / '_venture.json'
        meta = json.loads(meta_path.read_text())
        assert 'related' in meta
        assert len(meta['related']) > 0

    def test_venture_page_has_cross_links(self):
        self.agent.run(SAMPLE_DATA)
        page = Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'frankmax' / 'frankmax-talent' / 'index.html'
        content = page.read_text()
        assert 'Related Ventures' in content

    def test_finds_related_same_group(self):
        related = self.agent._find_related(SAMPLE_DATA['ventures'][0], SAMPLE_DATA)
        same_group = [r for r in related if r['reason'] == 'same-group']
        assert len(same_group) >= 1

    def test_build_global_nav_skips_non_group(self):
        data = {
            'groups': [
                {'id': 'frankmax', 'name': 'Frankmax', 'type': 'group'},
                {'id': 'not-a-group', 'name': 'Ignore Me', 'type': 'venture'},
            ],
            'ventures': SAMPLE_DATA['ventures'],
        }
        nav = self.agent._build_global_nav(data)
        assert len(nav['groups']) == 1
        assert nav['groups'][0]['label'] == 'Frankmax'

    def test_finds_cross_group_related_and_limits(self):
        data = {
            'groups': SAMPLE_DATA['groups'],
            'ventures': [
                {'id': 'v1', 'name': 'V1', 'parentId': 'g1'},
                {'id': 'v2', 'name': 'V2', 'parentId': 'g1'},
                {'id': 'v3', 'name': 'V3', 'parentId': 'g2'},
                {'id': 'v4', 'name': 'V4', 'parentId': 'g3'},
                {'id': 'v5', 'name': 'V5', 'parentId': 'g4'},
                {'id': 'v6', 'name': 'V6', 'parentId': 'g5'},
            ],
        }
        related = self.agent._find_related(data['ventures'][0], data)
        assert len(related) == 3
        assert any(r['reason'] == 'cross-group' for r in related)

    def test_ecosystem_flows_default_and_mapped(self):
        mapped = self.agent._get_ecosystem_flows('frankmax-talent', SAMPLE_DATA)
        default = self.agent._get_ecosystem_flows('unknown', SAMPLE_DATA)
        assert mapped['downstream'] == ['virginbay-services']
        assert default == {'upstream': [], 'downstream': []}

    def test_render_cross_links_empty(self):
        assert self.agent._render_cross_links([]) == ''

    def test_run_continues_when_venture_dir_missing(self):
        shutil.rmtree(Path(self.tmpdir) / 'sites' / 'leo-global-holdings' / 'frankmax' / 'frankmax-learning')
        result = self.agent.run(SAMPLE_DATA)
        assert result['success'] is True
        assert result['metadata_updated'] >= 1

    def test_iterations_tracked(self):
        self.agent.run(SAMPLE_DATA)
        assert self.agent.iteration_count > 0
