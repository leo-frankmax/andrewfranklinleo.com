import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.agent_base import AgentBase


class ContentWriter(AgentBase):
    """Agent 3: Fill in detailed content for offering and venture pages."""

    def __init__(self, data_root: str = '/data'):
        super().__init__('content-writer', data_root)
        self.sites_root = self.data_root / 'sites' / 'leo-global-holdings'

    def run(self, ventures_data: dict) -> dict:
        self.increment()
        result = {
            'pages_enriched': 0,
            'seo_generated': 0,
            'errors': [],
        }

        try:
            for venture in ventures_data.get('ventures', []):
                if self.should_stop():
                    break

                venture_id = venture.get('id', '')
                group_id = venture.get('parentId', '')
                venture_dir = self.sites_root / group_id / venture_id

                if not venture_dir.exists():
                    continue

                for offering in venture.get('offerings', []):
                    if self.should_stop():
                        break
                    self.increment()

                    offering_id = offering.get('id', '')
                    offering_dir = venture_dir / offering_id
                    index_path = offering_dir / 'index.html'

                    if not index_path.exists():
                        continue

                    # Enrich the offering page
                    content = self._generate_offering_content(offering, venture)
                    index_path.write_text(content)
                    result['pages_enriched'] += 1

                    # Generate SEO meta
                    seo = self._generate_seo_meta(offering, venture, group_id)
                    (offering_dir / '_seo.json').write_text(json.dumps(seo, indent=2))
                    result['seo_generated'] += 1

                # Enrich venture page
                venture_index = venture_dir / 'index.html'
                if venture_index.exists():
                    content = self._generate_venture_content(venture, group_id)
                    venture_index.write_text(content)
                    result['pages_enriched'] += 1

            result['success'] = True

        except Exception as e:
            self.emit_failure(e, {'pages_enriched': result['pages_enriched']})
            result['errors'].append(str(e))
            result['success'] = False

        return result

    def _generate_offering_content(self, offering: dict, venture: dict) -> str:
        name = offering.get('name', '')
        venture_name = venture.get('name', '')
        gid = venture.get('parentId', '')
        vid = venture.get('id', '')
        oid = offering.get('id', '')
        color = gid.split('-')[0] if gid else ''
        gname = gid.replace('-', ' ').title()
        odesc = offering.get('description', '')
        first = name[0] if name else 'O'
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} | {venture_name} | Leo Global Holdings</title>
  <link rel="stylesheet" href="/styles.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <meta name="description" content="{odesc[:160] if odesc else name}">
  <meta property="og:title" content="{name} | {venture_name}">
  <meta property="og:description" content="{odesc[:160] if odesc else ''}">
</head>
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>
  <nav aria-label="Breadcrumb" class="breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/{gid}/">{gname}</a></li><li><a href="/{gid}/{vid}/">{venture_name}</a></li><li><a href="/{gid}/{vid}/{oid}/" aria-current="page">{name}</a></li></ol></nav>
  <main id="main-content">
    <section class="hero group-{color} parallax">
      <div class="hero-bg" role="img" aria-label="{name}"></div>
      <span class="hero-tag">{venture_name}</span>
      <h1>{name}</h1>
      <p class="mission">Part of {venture_name} — delivering exceptional value to stakeholders through professional excellence and proven methodologies.</p>
    </section>
    <section class="content-section">
      <h2>About {name}</h2>
      <p>{name} is a core offering within {venture_name}, designed to deliver exceptional value to our stakeholders through professional excellence and proven methodologies.</p>
      <h2>Key Benefits</h2>
      <ul>
        <li>Professional excellence and industry expertise</li>
        <li>Proven methodologies with measurable outcomes</li>
        <li>Integrated solutions across the value chain</li>
        <li>Deep domain knowledge and global perspective</li>
      </ul>
      <h2>The {venture_name} Advantage</h2>
      <p>As part of {venture_name}, this offering leverages cross-functional collaboration, proprietary frameworks, and a worldwide network of professionals dedicated to delivering measurable results for every engagement.</p>
    </section>
  </main>
  <script src="/components.js" defer></script>
</body>
</html>"""

    def _generate_venture_content(self, venture: dict, group_id: str) -> str:
        name = venture.get('name', '')
        mission = venture.get('mission', '')
        vid = venture.get('id', '')
        color = group_id.split('-')[0] if group_id else ''
        gname = group_id.replace('-', ' ').title()
        tagline = mission.split('—')[0].strip() if '—' in mission else ''
        offerings_html = ''
        for o in venture.get('offerings', []):
            oid = o.get('id', '')
            oname = o.get('name', '')
            offerings_html += f'<a href="/{group_id}/{vid}/{oid}/" class="card fade-in"><h3>{oname}</h3></a>\n'

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} | Leo Global Holdings</title>
  <link rel="stylesheet" href="/styles.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <meta name="description" content="{mission[:160]}">
  <meta property="og:title" content="{name} | Leo Global Holdings">
  <meta property="og:description" content="{mission[:160]}">
</head>
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>
  <nav aria-label="Breadcrumb" class="breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/{group_id}/">{gname}</a></li><li><a href="/{group_id}/{vid}/" aria-current="page">{name}</a></li></ol></nav>
  <main id="main-content">
    <section class="hero group-{color} parallax">
      <div class="hero-bg" role="img" aria-label="{name}"></div>
      <span class="hero-tag">{tagline}</span>
      <h1>{name}</h1>
      <p class="mission">{mission}</p>
      <a href="#offerings" class="hero-cta btn-ripple">Our Offerings <span aria-hidden="true">&darr;</span></a>
      <div class="hero-scroll" aria-hidden="true"></div>
    </section>
    <section class="section" id="offerings">
      <div class="section-header"><h2>Our Offerings</h2></div>
      <div class="grid stagger">{offerings_html}</div>
    </section>
  </main>
  <script src="/components.js" defer></script>
</body>
</html>"""

    def _generate_seo_meta(self, offering: dict, venture: dict, group_id: str) -> dict:
        name = offering.get('name', '')
        return {
            'title': f'{name} | {venture.get("name", "")} | Leo Global Holdings',
            'description': f'{name} - part of {venture.get("name", "")}',
            'og_title': name,
            'og_description': f'{name} within {venture.get("name", "")}',
            'canonical': f'/{group_id}/{venture.get("id", "")}/{offering.get("id", "")}/',
        }


if __name__ == '__main__':
    data_root = '/data'
    ventures_path = Path(data_root) / 'ventures.json'

    if not ventures_path.exists():
        print(f'ERROR: {ventures_path} not found', file=sys.stderr)
        sys.exit(1)

    ventures_data = json.loads(ventures_path.read_text())
    agent = ContentWriter(data_root)
    result = agent.run(ventures_data)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get('success') else 1)
