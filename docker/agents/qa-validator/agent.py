import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.agent_base import AgentBase


class QaValidator(AgentBase):
    """Agent 5: Validate site structure, check for orphans, broken links."""

    def __init__(self, data_root: str = '/data'):
        super().__init__('qa-validator', data_root)
        self.sites_root = self.data_root / 'sites' / 'leo-global-holdings'

    def run(self, ventures_data: dict) -> dict:
        self.increment()
        result = {
            'pages_validated': 0,
            'orphan_pages': [],
            'broken_links': [],
            'missing_metadata': [],
            'validation_passed': True,
            'errors': [],
        }

        try:
            # Validate graph structure
            graph_result = self._validate_graph(ventures_data)
            result['orphan_pages'] = graph_result.get('orphans', [])

            # Validate all pages exist
            for venture in ventures_data.get('ventures', []):
                if self.should_stop():
                    break
                self.increment()

                group_id = venture.get('parentId', '')
                venture_id = venture.get('id', '')
                venture_dir = self.sites_root / group_id / venture_id

                # Check venture page
                venture_index = venture_dir / 'index.html'
                if venture_index.exists():
                    result['pages_validated'] += 1
                    content = venture_index.read_text()
                    if '<title>' not in content:
                        result['broken_links'].append(f'{venture_id}/index.html missing title')
                else:
                    result['orphan_pages'].append(f'{group_id}/{venture_id}/index.html')

                # Check metadata
                venture_meta = venture_dir / '_venture.json'
                if venture_meta.exists():
                    meta = json.loads(venture_meta.read_text())
                    if not meta.get('name'):
                        result['missing_metadata'].append(f'{venture_id}/_venture.json missing name')
                else:
                    result['missing_metadata'].append(f'{venture_id}/_venture.json')

                # Check offerings
                for offering in venture.get('offerings', []):
                    if self.should_stop():
                        break
                    self.increment()

                    offering_id = offering.get('id', '')
                    offering_dir = venture_dir / offering_id
                    offering_index = offering_dir / 'index.html'

                    if offering_index.exists():
                        result['pages_validated'] += 1
                    else:
                        result['orphan_pages'].append(f'{group_id}/{venture_id}/{offering_id}/index.html')

                    offering_meta = offering_dir / '_offering.json'
                    if not offering_meta.exists():
                        result['missing_metadata'].append(f'{offering_id}/_offering.json')

            result['validation_passed'] = (
                len(result['orphan_pages']) == 0 and
                len(result['broken_links']) == 0
            )
            result['success'] = True

        except Exception as e:
            self.emit_failure(e, {'pages_validated': result['pages_validated']})
            result['errors'].append(str(e))
            result['success'] = False

        return result

    def _validate_graph(self, data: dict) -> dict:
        orphans = []
        node_ids = set()

        # Collect all expected node IDs
        for group in data.get('groups', []):
            node_ids.add(group.get('id', ''))
        for venture in data.get('ventures', []):
            node_ids.add(venture.get('id', ''))
            for offering in venture.get('offerings', []):
                node_ids.add(offering.get('id', ''))

        # Check parent references
        for venture in data.get('ventures', []):
            parent = venture.get('parentId', '')
            if parent and parent not in node_ids:
                orphans.append(venture.get('id', ''))

        return {'orphans': orphans, 'total_nodes': len(node_ids)}


if __name__ == '__main__':
    data_root = '/data'
    ventures_path = Path(data_root) / 'ventures.json'

    if not ventures_path.exists():
        print(f'ERROR: {ventures_path} not found', file=sys.stderr)
        sys.exit(1)

    ventures_data = json.loads(ventures_path.read_text())
    agent = QaValidator(data_root)
    result = agent.run(ventures_data)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get('success') else 1)
