import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.agent_base import AgentBase


class GraphBuilder(AgentBase):
    """Agent 4: Build cross-references, navigation, related-venture links."""

    def __init__(self, data_root: str = '/data'):
        super().__init__('graph-builder', data_root)
        self.sites_root = self.data_root / 'sites' / 'leo-global-holdings'

    def run(self, ventures_data: dict) -> dict:
        self.increment()
        result = {
            'nav_updated': False,
            'cross_links_added': 0,
            'metadata_updated': 0,
            'errors': [],
        }

        try:
            # Build global navigation
            nav = self._build_global_nav(ventures_data)
            nav_path = self.sites_root / 'global-nav.json'
            nav_path.write_text(json.dumps(nav, indent=2))
            result['nav_updated'] = True

            # Build cross-links for each venture
            for venture in ventures_data.get('ventures', []):
                if self.should_stop():
                    break
                self.increment()

                venture_id = venture.get('id', '')
                group_id = venture.get('parentId', '')
                venture_dir = self.sites_root / group_id / venture_id

                if not venture_dir.exists():
                    continue

                # Find related ventures (same group + cross-group)
                related = self._find_related(venture, ventures_data)

                # Update venture metadata
                meta_path = venture_dir / '_venture.json'
                if meta_path.exists():
                    meta = json.loads(meta_path.read_text())
                else:
                    meta = {'id': venture_id, 'name': venture.get('name', '')}

                meta['related'] = related
                meta['ecosystem_flows'] = self._get_ecosystem_flows(venture_id, ventures_data)
                meta_path.write_text(json.dumps(meta, indent=2))
                result['metadata_updated'] += 1

                # Add cross-link section to venture page
                venture_index = venture_dir / 'index.html'
                if venture_index.exists():
                    content = venture_index.read_text()
                    if '</main>' in content:
                        cross_links_html = self._render_cross_links(related)
                        content = content.replace('</main>', f'{cross_links_html}\n</main>')
                        venture_index.write_text(content)
                        result['cross_links_added'] += 1

            result['success'] = True

        except Exception as e:
            self.emit_failure(e, {'nav_updated': result['nav_updated']})
            result['errors'].append(str(e))
            result['success'] = False

        return result

    def _build_global_nav(self, data: dict) -> dict:
        groups = []
        for g in data.get('groups', []):
            if g.get('type') != 'group':
                continue
            ventures = []
            for v in data.get('ventures', []):
                if v.get('parentId') == g.get('id'):
                    ventures.append({
                        'label': v.get('name', ''),
                        'url': f'/{g.get("id", "")}/{v.get("id", "")}/',
                    })
            groups.append({
                'label': g.get('name', ''),
                'url': f'/{g.get("id", "")}/',
                'mission': g.get('mission', ''),
                'ventures': ventures,
            })
        return {'home': {'label': 'Home', 'url': '/'}, 'groups': groups}

    def _find_related(self, venture: dict, data: dict) -> list[dict]:
        related = []
        group_id = venture.get('parentId', '')
        for v in data.get('ventures', []):
            if v.get('id') == venture.get('id'):
                continue
            if v.get('parentId') == group_id:
                related.append({'id': v.get('id'), 'name': v.get('name', ''), 'reason': 'same-group'})
            elif len(related) < 3:
                related.append({'id': v.get('id'), 'name': v.get('name', ''), 'reason': 'cross-group'})
        return related[:5]

    def _get_ecosystem_flows(self, venture_id: str, data: dict) -> dict:
        flows = {'upstream': [], 'downstream': []}
        flows_map = {
            'frankmax-talent': {'downstream': ['virginbay-services']},
            'virginbay-marketplace': {'downstream': ['glosbe-communities']},
            'glosbe-communities': {'downstream': ['crenza-wealth']},
        }
        if venture_id in flows_map:
            flows.update(flows_map[venture_id])
        return flows

    def _render_cross_links(self, related: list[dict]) -> str:
        if not related:
            return ''
        items = ''.join(f'<li><a href="/{r["id"]}/">{r["name"]}</a> <span>({r["reason"]})</span></li>' for r in related)
        return f'<section class="related"><h2>Related Ventures</h2><ul>{items}</ul></section>'


if __name__ == '__main__':
    data_root = '/data'
    ventures_path = Path(data_root) / 'ventures.json'

    if not ventures_path.exists():
        print(f'ERROR: {ventures_path} not found', file=sys.stderr)
        sys.exit(1)

    ventures_data = json.loads(ventures_path.read_text())
    agent = GraphBuilder(data_root)
    result = agent.run(ventures_data)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get('success') else 1)
