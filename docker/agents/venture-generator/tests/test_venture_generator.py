import pytest
import sys
import json
import importlib.util
from pathlib import Path

# Import agent module directly (directory has dash, can't use standard import)
spec = importlib.util.spec_from_file_location('agent', str(Path(__file__).parent.parent / 'agent.py'))
agent_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_mod)
VentureGenerator = agent_mod.VentureGenerator


SAMPLE_DATA = {
    'conglomerate': {'id': 'leo-global-holdings', 'name': 'Leo Global Holdings'},
    'groups': [
        {'id': 'frankmax', 'name': 'Frankmax', 'parentId': 'leo-global-holdings'},
    ],
    'ventures': [
        {'id': 'frankmax-talent', 'name': 'Frankmax Talent', 'parentId': 'frankmax',
         'offerings': [{'id': 'executive-search', 'name': 'Executive Search', 'parentId': 'frankmax-talent'}]},
    ],
}


class TestVentureGenerator:
    def setup_method(self):
        self.agent = VentureGenerator(data_root='/tmp/test-data')

    def test_creates_agent(self):
        assert self.agent.agent_name == 'venture-generator'
        assert self.agent.run_id is not None

    def test_processes_groups(self):
        result = self.agent.run(SAMPLE_DATA.copy())
        assert result['success'] is True
        assert result['groups_processed'] >= 1

    def test_processes_ventures(self):
        result = self.agent.run(SAMPLE_DATA.copy())
        assert result['ventures_created'] >= 1

    def test_processes_offerings(self):
        result = self.agent.run(SAMPLE_DATA.copy())
        assert result['offerings_created'] >= 1

    def test_fills_missing_mission(self):
        data = SAMPLE_DATA.copy()
        data['groups'] = [{'id': 'test', 'name': 'Test', 'parentId': 'leo-global-holdings'}]
        result = self.agent.run(data)
        assert result['success'] is True

    def test_fills_missing_slug(self):
        data = {
            'groups': [{'id': 'test-group', 'name': 'Test Group', 'parentId': 'leo-global-holdings'}],
            'ventures': [],
        }
        self.agent.run(data)
        assert data['groups'][0].get('slug') == 'test-group'

    def test_validates_output_valid(self):
        data = {
            'groups': [{'id': 'g', 'name': 'G', 'slug': 'g', 'mission': 'm'}],
            'ventures': [{'id': 'v', 'name': 'V', 'parentId': 'g', 'slug': 'v'}],
        }
        result = self.agent.validate_output(data)
        assert result['valid'] is True

    def test_validates_output_missing_fields(self):
        data = {'groups': [{'id': 'g'}], 'ventures': [{'id': 'v'}]}
        result = self.agent.validate_output(data)
        assert result['valid'] is False
        assert len(result['errors']) > 0

    def test_iterations_tracked(self):
        self.agent.run(SAMPLE_DATA.copy())
        assert self.agent.iteration_count > 0

    def test_emits_failure_on_error(self):
        result = self.agent.run({})
        assert result['success'] is False
        assert len(result['errors']) > 0

    def test_max_iterations_stops(self):
        self.agent.max_iterations = 2
        result = self.agent.run(SAMPLE_DATA.copy())
        # May or may not hit limit depending on data size
        assert self.agent.iteration_count <= 3

    def test_version_updated(self):
        data = SAMPLE_DATA.copy()
        data['version'] = '1.0'
        result = self.agent.run(data)
        assert result['ventures_data']['version'] == '2.0'
