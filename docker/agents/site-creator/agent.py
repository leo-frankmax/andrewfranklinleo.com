import json
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.agent_base import AgentBase
from shared.path_guard import PathGuard


class SiteCreator(AgentBase):
    """Agent 2: Create directory structure and landing pages for every node."""

    def __init__(self, data_root: str = '/data'):
        super().__init__('site-creator', data_root)
        self.path_guard = PathGuard()
        self.sites_root = self.data_root / 'sites' / 'leo-global-holdings'

    def run(self, ventures_data: dict) -> dict:
        self.increment()
        result = {
            'directories_created': 0,
            'pages_created': 0,
            'metadata_created': 0,
            'errors': [],
        }

        try:
            # Create conglomerate portal
            self._create_conglomerate_portal(ventures_data)
            result['pages_created'] += 1

            # Process each group
            for group in ventures_data.get('groups', []):
                if self.should_stop():
                    break
                self.increment()

                group_id = group.get('id', '')
                group_dir = self.sites_root / group_id
                group_dir.mkdir(parents=True, exist_ok=True)
                result['directories_created'] += 1

                # Write group metadata
                group_meta = {
                    'id': group_id,
                    'name': group.get('name', ''),
                    'type': group.get('type', 'group'),
                    'mission': group.get('mission', ''),
                    'parentId': group.get('parentId', ''),
                }
                meta_path = group_dir / '_group.json'
                meta_path.write_text(json.dumps(group_meta, indent=2))
                result['metadata_created'] += 1

                # Write group landing page
                group_html = self._render_group_page(group)
                (group_dir / 'index.html').write_text(group_html)
                result['pages_created'] += 1

                # Process ventures in this group
                for venture in ventures_data.get('ventures', []):
                    if venture.get('parentId') != group_id:
                        continue
                    if self.should_stop():
                        break

                    self.increment()
                    venture_id = venture.get('id', '')
                    venture_dir = group_dir / venture_id
                    venture_dir.mkdir(parents=True, exist_ok=True)
                    result['directories_created'] += 1

                    # Write venture metadata
                    venture_meta = {
                        'id': venture_id,
                        'name': venture.get('name', ''),
                        'type': 'venture',
                        'mission': venture.get('mission', ''),
                        'parentId': group_id,
                    }
                    (venture_dir / '_venture.json').write_text(json.dumps(venture_meta, indent=2))
                    result['metadata_created'] += 1

                    # Write venture landing page
                    venture_html = self._render_venture_page(venture, group)
                    (venture_dir / 'index.html').write_text(venture_html)
                    result['pages_created'] += 1

                    # Process offerings
                    for offering in venture.get('offerings', []):
                        if self.should_stop():
                            break
                        self.increment()

                        offering_id = offering.get('id', '')
                        offering_dir = venture_dir / offering_id
                        offering_dir.mkdir(parents=True, exist_ok=True)
                        result['directories_created'] += 1

                        # Write offering metadata
                        offering_meta = {
                            'id': offering_id,
                            'name': offering.get('name', ''),
                            'type': 'offering',
                            'parentId': venture_id,
                        }
                        (offering_dir / '_offering.json').write_text(json.dumps(offering_meta, indent=2))
                        result['metadata_created'] += 1

                        # Write offering page
                        offering_html = self._render_offering_page(offering, venture)
                        (offering_dir / 'index.html').write_text(offering_html)
                        result['pages_created'] += 1

            result['success'] = True

        except Exception as e:
            self.emit_failure(e, {'groups': len(ventures_data.get('groups', []))})
            result['errors'].append(str(e))
            result['success'] = False

        return result

    def _create_conglomerate_portal(self, data: dict):
        conglomerate = data.get('conglomerate', {})
        portal_dir = self.sites_root
        portal_dir.mkdir(parents=True, exist_ok=True)

        # Write conglomerate metadata
        meta = {
            'id': conglomerate.get('id', 'leo-global-holdings'),
            'name': conglomerate.get('name', 'Leo Global Holdings'),
            'type': 'conglomerate',
            'mission': conglomerate.get('mission', ''),
        }
        (portal_dir / '_conglomerate.json').write_text(json.dumps(meta, indent=2))

        # Write portal page
        groups_html = ''
        for group in data.get('groups', []):
            if group.get('type') == 'group':
                groups_html += f'<article class="card"><h3><a href="/{group["id"]}/">{group["name"]}</a></h3><p>{group.get("mission", "")}</p></article>\n'

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{meta['name']}</title>
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <main>
    <header class="hero">
      <h1>{meta['name']}</h1>
      <p class="mission">{meta['mission']}</p>
    </header>
    <section class="groups-section">
      <h2>Our Ecosystem</h2>
      <div class="grid">{groups_html}</div>
    </section>
  </main>
</body>
</html>"""
        (portal_dir / 'index.html').write_text(html)

    def _render_group_page(self, group: dict) -> str:
        ventures_html = ''
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{group.get('name', '')} | Leo Global Holdings</title>
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <nav aria-label="Breadcrumb" class="breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/{group.get('id', '')}/" aria-current="page">{group.get('name', '')}</a></li></ol></nav>
  <main>
    <header class="hero">
      <h1>{group.get('name', '')}</h1>
      <p class="mission">{group.get('mission', '')}</p>
    </header>
    <section><h2>Our Ventures</h2><div class="grid">{ventures_html}</div></section>
  </main>
</body>
</html>"""

    def _render_venture_page(self, venture: dict, group: dict) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{venture.get('name', '')} | {group.get('name', '')} | Leo Global Holdings</title>
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <nav aria-label="Breadcrumb" class="breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/{group.get('id', '')}/">{group.get('name', '')}</a></li><li><a href="/{group.get('id', '')}/{venture.get('id', '')}/" aria-current="page">{venture.get('name', '')}</a></li></ol></nav>
  <main>
    <header class="hero">
      <h1>{venture.get('name', '')}</h1>
      <p class="mission">{venture.get('mission', '')}</p>
    </header>
    <section><h2>Our Offerings</h2><div class="grid"></div></section>
  </main>
</body>
</html>"""

    def _render_offering_page(self, offering: dict, venture: dict) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{offering.get('name', '')} | {venture.get('name', '')} | Leo Global Holdings</title>
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <nav aria-label="Breadcrumb" class="breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/{venture.get('parentId', '')}/">{venture.get('parentId', '')}</a></li><li><a href="/{venture.get('parentId', '')}/{venture.get('id', '')}/">{venture.get('name', '')}</a></li><li><a href="/{venture.get('parentId', '')}/{venture.get('id', '')}/{offering.get('id', '')}/" aria-current="page">{offering.get('name', '')}</a></li></ol></nav>
  <main>
    <header class="hero">
      <h1>{offering.get('name', '')}</h1>
    </header>
    <section class="content"><p>Content for {offering.get('name', '')}</p></section>
  </main>
</body>
</html>"""


if __name__ == '__main__':
    data_root = '/data'
    ventures_path = Path(data_root) / 'ventures.json'

    if not ventures_path.exists():
        print(f'ERROR: {ventures_path} not found', file=sys.stderr)
        sys.exit(1)

    ventures_data = json.loads(ventures_path.read_text())
    agent = SiteCreator(data_root)
    result = agent.run(ventures_data)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get('success') else 1)
