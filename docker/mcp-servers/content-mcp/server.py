import os
import json
from typing import Any


class ContentMcpServer:
    def __init__(self, api_key: str | None = None, model: str = 'gpt-4.1'):
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY', '')
        self.model = model

    def generate_venture_description(self, venture_data: dict) -> dict:
        name = venture_data.get('name', 'Unknown')
        mission = venture_data.get('mission', '')
        offerings = venture_data.get('offerings', [])

        content = f"""<h1>{name}</h1>
<p class="mission">{mission}</p>

<h2>What We Offer</h2>
<ul>
{''.join(f'<li>{o.get("name", "")}</li>' for o in offerings)}
</ul>

<h2>Our Impact</h2>
<p>{name} is committed to {mission.lower()}. Through our comprehensive suite of offerings, we deliver measurable results for our stakeholders.</p>"""

        return {'content': content, 'word_count': len(content.split())}

    def generate_offering_description(self, offering_data: dict) -> dict:
        name = offering_data.get('name', 'Unknown')
        venture_name = offering_data.get('venture_name', '')

        content = f"""<h1>{name}</h1>
<p class="offering-venture">Part of {venture_name}</p>

<h2>About {name}</h2>
<p>{name} is a core offering within {venture_name}, designed to deliver exceptional value to our stakeholders.</p>

<h2>Key Benefits</h2>
<ul>
<li>Professional excellence</li>
<li>Proven methodologies</li>
<li>Measurable outcomes</li>
</ul>"""

        return {'content': content, 'word_count': len(content.split())}

    def generate_seo_meta(self, page_data: dict) -> dict:
        title = page_data.get('title', '')
        description = page_data.get('description', '')
        url = page_data.get('url', '')

        return {
            'title': f'{title} | Andrew Franklin Leo',
            'description': description,
            'og_title': title,
            'og_description': description,
            'og_image': '/assets/og-default.png',
            'canonical': url,
            'json_ld': {
                '@context': 'https://schema.org',
                '@type': 'Organization',
                'name': title,
                'description': description,
            },
        }

    def generate_biography(self, person_data: dict) -> dict:
        name = person_data.get('name', '')
        role = person_data.get('role', '')

        return {
            'content': f"""<h1>{name}</h1>
<p class="role">{role}</p>
<p>{name} is a visionary leader dedicated to building the future of human potential through the Andrew Franklin Leo ecosystem.</p>""",
            'word_count': 50,
        }

    def generate_mission_statement(self, entity_data: dict) -> dict:
        name = entity_data.get('name', '')
        purpose = entity_data.get('purpose', '')

        return {
            'mission': f'{name} exists to {purpose}',
            'vision': f'A world where {purpose} transforms lives and communities.',
        }

    def generate_group_overview(self, group_data: dict) -> dict:
        name = group_data.get('name', '')
        mission = group_data.get('mission', '')
        ventures = group_data.get('ventures', [])

        return {
            'content': f"""<h1>{name}</h1>
<p class="mission">{mission}</p>

<h2>Our Ventures</h2>
<p>{name} encompasses {len(ventures)} ventures, each dedicated to advancing our mission.</p>""",
            'word_count': 40,
        }

    def expand_venture_list(self, group: dict, master_prompt: str) -> dict:
        return {
            'ventures': group.get('ventures', []),
            'expanded': False,
            'note': 'Expansion requires LLM API call',
        }

    def generate_breadcrumb_trail(self, node_data: dict) -> dict:
        path = node_data.get('path', '')
        parts = [p for p in path.split('/') if p]
        crumbs = [{'label': 'Home', 'url': '/'}]
        for i, part in enumerate(parts):
            crumbs.append({
                'label': part.replace('-', ' ').title(),
                'url': '/' + '/'.join(parts[:i + 1]) + '/',
            })
        return {'breadcrumbs': crumbs}


TOOLS = {
    'generate_venture_description': {
        'description': 'Generate full venture page content',
        'inputSchema': {
            'type': 'object',
            'properties': {'venture_data': {'type': 'object'}},
            'required': ['venture_data'],
        },
    },
    'generate_offering_description': {
        'description': 'Generate product/service/solution page',
        'inputSchema': {
            'type': 'object',
            'properties': {'offering_data': {'type': 'object'}},
            'required': ['offering_data'],
        },
    },
    'generate_seo_meta': {
        'description': 'Generate meta tags, JSON-LD',
        'inputSchema': {
            'type': 'object',
            'properties': {'page_data': {'type': 'object'}},
            'required': ['page_data'],
        },
    },
    'generate_biography': {
        'description': 'Write executive/founder biography',
        'inputSchema': {
            'type': 'object',
            'properties': {'person_data': {'type': 'object'}},
            'required': ['person_data'],
        },
    },
    'generate_mission_statement': {
        'description': 'Create mission/vision text',
        'inputSchema': {
            'type': 'object',
            'properties': {'entity_data': {'type': 'object'}},
            'required': ['entity_data'],
        },
    },
    'generate_group_overview': {
        'description': 'Write group landing page content',
        'inputSchema': {
            'type': 'object',
            'properties': {'group_data': {'type': 'object'}},
            'required': ['group_data'],
        },
    },
    'expand_venture_list': {
        'description': 'Apply master prompt to generate new ventures',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'group': {'type': 'object'},
                'master_prompt': {'type': 'string'},
            },
            'required': ['group', 'master_prompt'],
        },
    },
    'generate_breadcrumb_trail': {
        'description': 'Create breadcrumb text',
        'inputSchema': {
            'type': 'object',
            'properties': {'node_data': {'type': 'object'}},
            'required': ['node_data'],
        },
    },
}
