import os
import json
import re
from pathlib import Path
from typing import Any


class TemplateMcpServer:
    def __init__(self, templates_dir: str = '/app/templates'):
        self.templates_dir = Path(templates_dir)
        self.globals = {
            'site_name': 'Andrew Franklin Leo',
            'site_url': 'https://andrewfranklinleo.com',
            'theme': 'professional',
            'colors': {
                'primary': '#1a365d',
                'secondary': '#2563eb',
                'accent': '#f59e0b',
            },
        }

    def render_template(self, template_name: str, variables: dict) -> dict:
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f'Template not found: {template_name}')
        template = template_path.read_text(encoding='utf-8')
        rendered = self._interpolate(template, {**self.globals, **variables})
        return {'html': rendered, 'template': template_name}

    def get_template(self, name: str) -> dict:
        template_path = self.templates_dir / name
        if not template_path.exists():
            raise FileNotFoundError(f'Template not found: {name}')
        return {'content': template_path.read_text(encoding='utf-8'), 'name': name}

    def list_templates(self) -> dict:
        if not self.templates_dir.exists():
            return {'templates': []}
        templates = []
        for f in sorted(self.templates_dir.glob('*.html')):
            templates.append({'name': f.name, 'size': f.stat().st_size})
        return {'templates': templates}

    def apply_global_layout(self, content: str, title: str) -> dict:
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | {self.globals['site_name']}</title>
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <main>{content}</main>
</body>
</html>"""
        return {'html': html}

    def render_breadcrumb(self, nodes: list[dict]) -> dict:
        items = []
        for i, node in enumerate(nodes):
            is_last = i == len(nodes) - 1
            items.append(f'<li><a href="{node["url"]}"{" aria-current=\"page\"" if is_last else ""}>{node["label"]}</a></li>')
        html = f'<nav aria-label="Breadcrumb" class="breadcrumb"><ol>{"".join(items)}</ol></nav>'
        return {'html': html}

    def render_nav(self, current_group: str = '', current_venture: str = '') -> dict:
        return {'html': '<nav class="global-nav"><ul><li><a href="/">Home</a></li></ul></nav>'}

    def render_card(self, data: dict, card_type: str = 'venture') -> dict:
        html = f"""<article class="card">
  <div class="card-icon" aria-hidden="true">{data.get('icon', '')}</div>
  <h3><a href="{data.get('url', '#')}">{data.get('title', '')}</a></h3>
  <p>{data.get('description', '')}</p>
</article>"""
        return {'html': html}

    def validate_html(self, html: str) -> dict:
        issues = []
        if '<script' in html.lower():
            issues.append('Script tags detected')
        if 'onerror=' in html.lower():
            issues.append('Event handlers detected')
        if html.count('<p') != html.count('</p'):
            issues.append('Mismatched <p> tags')
        return {'valid': len(issues) == 0, 'issues': issues}

    def _interpolate(self, template: str, context: dict) -> str:
        result = template
        for key, value in context.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    result = result.replace('{{' + key + '.' + sub_key + '}}', str(sub_value))
            else:
                result = result.replace('{{' + key + '}}', str(value))
        result = re.sub(r'\{\{[^}]+\}\}', '', result)
        return result


TOOLS = {
    'render_template': {
        'description': 'Render template with variables',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'template_name': {'type': 'string'},
                'variables': {'type': 'object'},
            },
            'required': ['template_name', 'variables'],
        },
    },
    'get_template': {
        'description': 'Get template content',
        'inputSchema': {
            'type': 'object',
            'properties': {'name': {'type': 'string'}},
            'required': ['name'],
        },
    },
    'list_templates': {
        'description': 'List available templates',
        'inputSchema': {'type': 'object', 'properties': {}},
    },
    'apply_global_layout': {
        'description': 'Wrap content in base layout',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'content': {'type': 'string'},
                'title': {'type': 'string'},
            },
            'required': ['content', 'title'],
        },
    },
    'render_breadcrumb': {
        'description': 'Render breadcrumb HTML',
        'inputSchema': {
            'type': 'object',
            'properties': {'nodes': {'type': 'array'}},
            'required': ['nodes'],
        },
    },
    'render_nav': {
        'description': 'Render navigation HTML',
        'inputSchema': {'type': 'object', 'properties': {}},
    },
    'render_card': {
        'description': 'Render venture/offering card',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'data': {'type': 'object'},
                'card_type': {'type': 'string'},
            },
            'required': ['data'],
        },
    },
    'validate_html': {
        'description': 'Basic HTML validation',
        'inputSchema': {
            'type': 'object',
            'properties': {'html': {'type': 'string'}},
            'required': ['html'],
        },
    },
}
