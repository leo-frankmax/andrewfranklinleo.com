import pytest
from pathlib import Path

from server import ContentMcpServer


class TestContentMcp:
    def setup_method(self):
        self.server = ContentMcpServer(api_key='test-key')

    def test_generate_venture_description(self):
        result = self.server.generate_venture_description({
            'name': 'Frankmax Talent',
            'mission': 'Recruit world-class professionals',
            'offerings': [{'name': 'Executive Search'}, {'name': 'Recruitment'}],
        })
        assert 'Frankmax Talent' in result['content']
        assert 'Executive Search' in result['content']
        assert result['word_count'] > 0

    def test_generate_offering_description(self):
        result = self.server.generate_offering_description({
            'name': 'Executive Search',
            'venture_name': 'Frankmax Talent',
        })
        assert 'Executive Search' in result['content']
        assert 'Frankmax Talent' in result['content']

    def test_generate_seo_meta(self):
        result = self.server.generate_seo_meta({
            'title': 'Frankmax Talent',
            'description': 'Recruit world-class professionals',
            'url': '/frankmax/frankmax-talent/',
        })
        assert result['title'] == 'Frankmax Talent | Andrew Franklin Leo'
        assert result['og_title'] == 'Frankmax Talent'
        assert result['json_ld']['@type'] == 'Organization'

    def test_generate_biography(self):
        result = self.server.generate_biography({
            'name': 'Andrew Franklin Leo',
            'role': 'Founder & CEO',
        })
        assert 'Andrew Franklin Leo' in result['content']
        assert 'Founder' in result['content']

    def test_generate_mission_statement(self):
        result = self.server.generate_mission_statement({
            'name': 'Frankmax',
            'purpose': 'empower every professional',
        })
        assert 'empower every professional' in result['mission']
        assert 'vision' in result

    def test_generate_group_overview(self):
        result = self.server.generate_group_overview({
            'name': 'Frankmax',
            'mission': 'Empowering Every Professional',
            'ventures': [{'name': 'A'}, {'name': 'B'}],
        })
        assert 'Frankmax' in result['content']
        assert '2 ventures' in result['content']

    def test_generate_breadcrumb_trail(self):
        result = self.server.generate_breadcrumb_trail({
            'path': 'frankmax/frankmax-talent/executive-search',
        })
        crumbs = result['breadcrumbs']
        assert len(crumbs) == 4
        assert crumbs[0]['label'] == 'Home'
        assert crumbs[3]['url'] == '/frankmax/frankmax-talent/executive-search/'
