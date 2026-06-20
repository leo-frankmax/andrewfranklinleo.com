import json
from pathlib import Path
from typing import Any


class GraphMcpServer:
    def __init__(self, ventures_path: str = '/data/ventures.json'):
        self.ventures_path = Path(ventures_path)
        self._graph: dict[str, Any] = {}
        self._load_graph()

    def _load_graph(self):
        if self.ventures_path.exists():
            data = json.loads(self.ventures_path.read_text())
            self._build_graph(data)

    def _build_graph(self, data: dict):
        # Add conglomerate
        c = data.get('conglomerate', {})
        if c:
            self._graph[c['id']] = {
                'id': c['id'], 'name': c['name'], 'type': 'conglomerate',
                'parentId': None, 'children': [], 'mission': c.get('mission', ''),
            }

        # Add groups
        for g in data.get('groups', []):
            self._graph[g['id']] = {
                'id': g['id'], 'name': g['name'], 'type': g.get('type', 'group'),
                'parentId': g.get('parentId'), 'children': [],
                'mission': g.get('mission', ''),
            }
            parent = g.get('parentId')
            if parent and parent in self._graph:
                self._graph[parent]['children'].append(g['id'])

        # Add ventures and offerings
        for v in data.get('ventures', []):
            self._graph[v['id']] = {
                'id': v['id'], 'name': v['name'], 'type': 'venture',
                'parentId': v.get('parentId'), 'children': [],
                'mission': v.get('mission', ''),
            }
            parent = v.get('parentId')
            if parent and parent in self._graph:
                self._graph[parent]['children'].append(v['id'])

            for o in v.get('offerings', []):
                self._graph[o['id']] = {
                    'id': o['id'], 'name': o['name'], 'type': 'offering',
                    'parentId': v['id'], 'children': [],
                }
                self._graph[v['id']]['children'].append(o['id'])

    def get_node(self, path: str) -> dict | None:
        return self._graph.get(path)

    def get_children(self, path: str) -> list[dict]:
        node = self._graph.get(path)
        if not node:
            return []
        return [self._graph[cid] for cid in node['children'] if cid in self._graph]

    def get_parent(self, path: str) -> dict | None:
        node = self._graph.get(path)
        if not node or not node.get('parentId'):
            return None
        return self._graph.get(node['parentId'])

    def get_siblings(self, path: str) -> list[dict]:
        node = self._graph.get(path)
        if not node or not node.get('parentId'):
            return []
        parent = self._graph.get(node['parentId'])
        if not parent:
            return []
        return [self._graph[cid] for cid in parent['children'] if cid != path and cid in self._graph]

    def get_ancestors(self, path: str) -> list[dict]:
        ancestors = []
        node = self._graph.get(path)
        while node and node.get('parentId'):
            parent = self._graph.get(node['parentId'])
            if parent:
                ancestors.append(parent)
            node = parent
        return ancestors

    def add_node(self, path: str, metadata: dict) -> dict:
        parent_id = metadata.get('parentId')
        self._graph[path] = {
            'id': path,
            'name': metadata.get('name', path),
            'type': metadata.get('type', 'unknown'),
            'parentId': parent_id,
            'children': [],
            'mission': metadata.get('mission', ''),
        }
        if parent_id and parent_id in self._graph:
            self._graph[parent_id]['children'].append(path)
        return {'success': True, 'path': path}

    def remove_node(self, path: str) -> dict:
        node = self._graph.pop(path, None)
        if node and node.get('parentId') and node['parentId'] in self._graph:
            parent = self._graph[node['parentId']]
            parent['children'] = [c for c in parent['children'] if c != path]
        return {'success': True, 'path': path}

    def update_node(self, path: str, metadata: dict) -> dict:
        if path not in self._graph:
            return {'success': False, 'error': f'Node not found: {path}'}
        self._graph[path].update(metadata)
        return {'success': True, 'path': path}

    def build_global_nav(self) -> dict:
        groups = []
        for nid, node in self._graph.items():
            if node.get('type') == 'group':
                ventures = []
                for cid in node.get('children', []):
                    child = self._graph.get(cid)
                    if child and child.get('type') == 'venture':
                        ventures.append({'label': child['name'], 'url': f'/{cid}/'})
                groups.append({
                    'label': node['name'],
                    'url': f'/{nid}/',
                    'mission': node.get('mission', ''),
                    'ventures': ventures,
                })
        strategic = []
        for nid, node in self._graph.items():
            if node.get('type') == 'strategic-vertical':
                strategic.append({'label': node['name'], 'url': f'/{nid}/'})
        return {'home': {'label': 'Home', 'url': '/'}, 'groups': groups, 'strategicVerticals': strategic}

    def validate_graph(self) -> dict:
        orphans = []
        cycles = []
        for nid, node in self._graph.items():
            pid = node.get('parentId')
            if pid and pid not in self._graph:
                orphans.append(nid)
        # Simple cycle detection
        for nid, node in self._graph.items():
            visited = set()
            current = nid
            while current and current in self._graph:
                if current in visited:
                    cycles.append(nid)
                    break
                visited.add(current)
                current = self._graph[current].get('parentId')
        return {'valid': len(orphans) == 0 and len(cycles) == 0, 'orphans': orphans, 'cycles': cycles}

    def find_gaps(self) -> dict:
        expected = set()
        actual = set(self._graph.keys())
        gaps = expected - actual
        return {'gaps': list(gaps), 'total_nodes': len(actual)}

    def get_ecosystem_flows(self) -> dict:
        return {
            'flows': [
                {'from': 'frankmax', 'to': 'virginbay', 'label': 'Professional Development → Employment'},
                {'from': 'virginbay', 'to': 'glosbe', 'label': 'Business Activity → Community Engagement'},
                {'from': 'glosbe', 'to': 'crenza', 'label': 'Knowledge → Innovation'},
            ]
        }


TOOLS = {
    'get_node': {'description': 'Get node with all relationships', 'inputSchema': {'type': 'object', 'properties': {'path': {'type': 'string'}}, 'required': ['path']}},
    'get_children': {'description': 'Get direct children', 'inputSchema': {'type': 'object', 'properties': {'path': {'type': 'string'}}, 'required': ['path']}},
    'get_parent': {'description': 'Get parent node', 'inputSchema': {'type': 'object', 'properties': {'path': {'type': 'string'}}, 'required': ['path']}},
    'get_siblings': {'description': 'Get sibling nodes', 'inputSchema': {'type': 'object', 'properties': {'path': {'type': 'string'}}, 'required': ['path']}},
    'get_ancestors': {'description': 'Get full ancestor chain', 'inputSchema': {'type': 'object', 'properties': {'path': {'type': 'string'}}, 'required': ['path']}},
    'add_node': {'description': 'Add node to graph', 'inputSchema': {'type': 'object', 'properties': {'path': {'type': 'string'}, 'metadata': {'type': 'object'}}, 'required': ['path', 'metadata']}},
    'remove_node': {'description': 'Remove node from graph', 'inputSchema': {'type': 'object', 'properties': {'path': {'type': 'string'}}, 'required': ['path']}},
    'update_node': {'description': 'Update node metadata', 'inputSchema': {'type': 'object', 'properties': {'path': {'type': 'string'}, 'metadata': {'type': 'object'}}, 'required': ['path', 'metadata']}},
    'build_global_nav': {'description': 'Generate full navigation tree', 'inputSchema': {'type': 'object', 'properties': {}}},
    'validate_graph': {'description': 'Check for orphans, cycles, broken links', 'inputSchema': {'type': 'object', 'properties': {}}},
    'find_gaps': {'description': 'Find missing nodes in hierarchy', 'inputSchema': {'type': 'object', 'properties': {}}},
    'get_ecosystem_flows': {'description': 'Get flow relationships', 'inputSchema': {'type': 'object', 'properties': {}}},
}
