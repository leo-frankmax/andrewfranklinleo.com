import pytest
import tempfile
import json
import os
from pathlib import Path

from server import GraphMcpServer


SAMPLE_DATA = {
    'conglomerate': {'id': 'leo-global-holdings', 'name': 'Leo Global Holdings', 'mission': 'Test'},
    'groups': [
        {'id': 'frankmax', 'name': 'Frankmax', 'type': 'group', 'parentId': 'leo-global-holdings', 'mission': 'Empowering'},
        {'id': 'leo-technologies', 'name': 'Leo Technologies', 'type': 'strategic-vertical', 'parentId': 'leo-global-holdings'},
    ],
    'ventures': [
        {'id': 'frankmax-talent', 'name': 'Frankmax Talent', 'parentId': 'frankmax', 'mission': 'Recruit',
         'offerings': [
             {'id': 'executive-search', 'name': 'Executive Search', 'parentId': 'frankmax-talent'},
             {'id': 'recruitment', 'name': 'Recruitment', 'parentId': 'frankmax-talent'},
         ]},
    ],
}


class TestGraphMcp:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.ventures_path = os.path.join(self.tmpdir, 'ventures.json')
        with open(self.ventures_path, 'w') as f:
            json.dump(SAMPLE_DATA, f)
        self.server = GraphMcpServer(self.ventures_path)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_get_node(self):
        node = self.server.get_node('frankmax')
        assert node is not None
        assert node['name'] == 'Frankmax'

    def test_get_children(self):
        children = self.server.get_children('leo-global-holdings')
        ids = [c['id'] for c in children]
        assert 'frankmax' in ids

    def test_get_parent(self):
        parent = self.server.get_parent('frankmax')
        assert parent is not None
        assert parent['id'] == 'leo-global-holdings'

    def test_get_siblings(self):
        siblings = self.server.get_siblings('frankmax')
        ids = [s['id'] for s in siblings]
        assert 'leo-technologies' in ids

    def test_get_ancestors(self):
        ancestors = self.server.get_ancestors('executive-search')
        ids = [a['id'] for a in ancestors]
        assert 'frankmax-talent' in ids
        assert 'frankmax' in ids

    def test_add_node(self):
        result = self.server.add_node('new-venture', {
            'name': 'New Venture', 'type': 'venture', 'parentId': 'frankmax',
        })
        assert result['success'] is True
        node = self.server.get_node('new-venture')
        assert node['name'] == 'New Venture'

    def test_remove_node(self):
        result = self.server.remove_node('recruitment')
        assert result['success'] is True
        assert self.server.get_node('recruitment') is None

    def test_update_node(self):
        result = self.server.update_node('frankmax', {'mission': 'Updated'})
        assert result['success'] is True
        assert self.server.get_node('frankmax')['mission'] == 'Updated'

    def test_build_global_nav(self):
        nav = self.server.build_global_nav()
        assert len(nav['groups']) >= 1
        group_names = [g['label'] for g in nav['groups']]
        assert 'Frankmax' in group_names

    def test_validate_graph_valid(self):
        result = self.server.validate_graph()
        assert result['valid'] is True
        assert len(result['orphans']) == 0

    def test_validate_graph_orphan(self):
        self.server._graph['orphan'] = {'id': 'orphan', 'parentId': 'nonexistent', 'children': []}
        result = self.server.validate_graph()
        assert result['valid'] is False
        assert 'orphan' in result['orphans']

    def test_find_gaps(self):
        result = self.server.find_gaps()
        assert 'gaps' in result
        assert 'total_nodes' in result

    def test_get_ecosystem_flows(self):
        result = self.server.get_ecosystem_flows()
        assert len(result['flows']) >= 1
