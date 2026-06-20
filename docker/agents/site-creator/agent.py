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

        meta = {
            'id': conglomerate.get('id', 'leo-global-holdings'),
            'name': conglomerate.get('name', 'Leo Global Holdings'),
            'type': 'conglomerate',
            'mission': conglomerate.get('mission', ''),
        }
        (portal_dir / '_conglomerate.json').write_text(json.dumps(meta, indent=2))

        venture_count = sum(len(g.get('ventures', [])) for g in data.get('groups', []))
        offering_count = sum(
            len(v.get('offerings', []))
            for g in data.get('groups', [])
            for v in g.get('ventures', [])
        )

        groups_html = ''
        for group in data.get('groups', []):
            if group.get('type') == 'group':
                gid = group.get('id', '')
                color = gid.split('-')[0] if gid else ''
                ventures_links = ''.join(
                    f'<span>{v.get("name", "")}</span>'
                    for v in data.get('ventures', [])
                    if v.get('parentId') == gid
                )[:300]
                groups_html += f'''<a href="/{gid}/" class="ecosystem-card {color} fade-in">
          <div class="card-label">{group.get("mission", "").split("—")[0].strip() if "—" in group.get("mission", "") else ""}</div>
          <h3>{group.get("name", "")}</h3>
          <p class="mission">{group.get("mission", "")}</p>
          <div class="ventures-list">{ventures_links}</div>
        </a>\n'''

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{meta['name']} | Enterprise Ecosystem</title>
  <link rel="stylesheet" href="/styles.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
  <main>
    <section class="hero">
      <span class="hero-tag">Enterprise Ecosystem</span>
      <h1>{meta['name']}</h1>
      <p class="mission">{meta['mission']}</p>
    </section>
    <section class="stats-bar">
      <div class="stats-grid">
        <div class="stat-item fade-in"><div class="stat-number">{len(data.get('groups', []))}</div><div class="stat-label">Ecosystem Pillars</div></div>
        <div class="stat-item fade-in"><div class="stat-number">{venture_count}</div><div class="stat-label">Active Ventures</div></div>
        <div class="stat-item fade-in"><div class="stat-number">{offering_count}+</div><div class="stat-label">Global Offerings</div></div>
      </div>
    </section>
    <section class="section">
      <div class="section-header"><h2>Our Ecosystem</h2><p>Four pillars of enterprise excellence, each driving transformation across its domain.</p></div>
      <div class="ecosystem-grid">{groups_html}</div>
    </section>
  </main>
  <script src="/components.js"></script>
</body>
</html>"""
        (portal_dir / 'index.html').write_text(html)

    def _render_group_page(self, group: dict) -> str:
        gid = group.get('id', '')
        color = gid.split('-')[0] if gid else ''
        ventures_html = ''
        for venture in group.get('ventures', []):
            vid = venture.get('id', '')
            vname = venture.get('name', '')
            vmission = venture.get('mission', '')
            ventures_html += f'<a href="/{gid}/{vid}/" class="card fade-in"><div class="card-icon">{vname[0] if vname else "V"}</div><h3>{vname}</h3><p>{vmission}</p></a>\n'

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{group.get('name', '')} | Leo Global Holdings</title>
  <link rel="stylesheet" href="/styles.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
  <nav aria-label="Breadcrumb" class="breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/{gid}/" aria-current="page">{group.get('name', '')}</a></li></ol></nav>
  <main>
    <section class="hero group-{color}">
      <span class="hero-tag">{group.get('mission', '').split('—')[0].strip() if '—' in group.get('mission', '') else ''}</span>
      <h1>{group.get('name', '')}</h1>
      <p class="mission">{group.get('mission', '')}</p>
    </section>
    <section class="section">
      <div class="section-header"><h2>Our Ventures</h2></div>
      <div class="grid">{ventures_html}</div>
    </section>
  </main>
  <script src="/components.js"></script>
</body>
</html>"""

    def _render_venture_page(self, venture: dict, group: dict) -> str:
        gid = group.get('id', '')
        vid = venture.get('id', '')
        color = gid.split('-')[0] if gid else ''
        offerings_html = ''
        for offering in venture.get('offerings', []):
            oid = offering.get('id', '')
            oname = offering.get('name', '')
            odesc = offering.get('description', '')
            offerings_html += f'<a href="/{gid}/{vid}/{oid}/" class="card fade-in"><h3>{oname}</h3><p>{odesc}</p></a>\n'

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{venture.get('name', '')} | {group.get('name', '')} | Leo Global Holdings</title>
  <link rel="stylesheet" href="/styles.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
  <nav aria-label="Breadcrumb" class="breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/{gid}/">{group.get('name', '')}</a></li><li><a href="/{gid}/{vid}/" aria-current="page">{venture.get('name', '')}</a></li></ol></nav>
  <main>
    <section class="hero group-{color}">
      <span class="hero-tag">{venture.get('mission', '').split('—')[0].strip() if '—' in venture.get('mission', '') else ''}</span>
      <h1>{venture.get('name', '')}</h1>
      <p class="mission">{venture.get('mission', '')}</p>
    </section>
    <section class="section">
      <div class="section-header"><h2>Our Offerings</h2></div>
      <div class="grid">{offerings_html}</div>
    </section>
  </main>
  <script src="/components.js"></script>
</body>
</html>"""

    def _render_offering_page(self, offering: dict, venture: dict) -> str:
        vid = venture.get('id', '')
        gid = venture.get('parentId', '')
        oid = offering.get('id', '')
        color = gid.split('-')[0] if gid else ''

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{offering.get('name', '')} | {venture.get('name', '')} | Leo Global Holdings</title>
  <link rel="stylesheet" href="/styles.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
  <nav aria-label="Breadcrumb" class="breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/{gid}/">{gid.replace('-', ' ').title()}</a></li><li><a href="/{gid}/{vid}/">{venture.get('name', '')}</a></li><li><a href="/{gid}/{vid}/{oid}/" aria-current="page">{offering.get('name', '')}</a></li></ol></nav>
  <main>
    <section class="hero group-{color}">
      <span class="hero-tag">{venture.get('name', '')}</span>
      <h1>{offering.get('name', '')}</h1>
      <p class="mission">{offering.get('description', '')}</p>
    </section>
    <section class="content-section">
      <h2>About {offering.get('name', '')}</h2>
      <p>{offering.get('description', '')}</p>
      <h2>Key Capabilities</h2>
      <ul>
        <li>Industry-leading expertise and global reach</li>
        <li>Data-driven approach with measurable outcomes</li>
        <li>Integrated solutions across the value chain</li>
      </ul>
    </section>
  </main>
  <script src="/components.js"></script>
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
