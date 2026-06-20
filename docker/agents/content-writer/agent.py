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
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} | {venture_name} | Leo Global Holdings</title>
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <nav aria-label="Breadcrumb" class="breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/{venture.get('parentId', '')}/">{venture.get('parentId', '')}</a></li><li><a href="/{venture.get('parentId', '')}/{venture.get('id', '')}/">{venture_name}</a></li><li><a href="/{venture.get('parentId', '')}/{venture.get('id', '')}/{offering.get('id', '')}/" aria-current="page">{name}</a></li></ol></nav>
  <main>
    <header class="hero">
      <h1>{name}</h1>
      <p class="description">Part of {venture_name}</p>
    </header>
    <section class="content">
      <h2>About {name}</h2>
      <p>{name} is a core offering within {venture_name}, designed to deliver exceptional value to our stakeholders.</p>
      <h2>Key Benefits</h2>
      <ul>
        <li>Professional excellence</li>
        <li>Proven methodologies</li>
        <li>Measurable outcomes</li>
      </ul>
      <h2>Use Cases</h2>
      <p>Organizations across industries leverage {name} to achieve their strategic objectives.</p>
    </section>
  </main>
</body>
</html>"""

    def _generate_venture_content(self, venture: dict, group_id: str) -> str:
        name = venture.get('name', '')
        mission = venture.get('mission', '')
        offerings_html = ''
        for o in venture.get('offerings', []):
            offerings_html += f'<article class="card"><h3><a href="/{group_id}/{venture.get("id", "")}/{o.get("id", "")}/">{o.get("name", "")}</a></h3></article>\n'

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} | Leo Global Holdings</title>
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <nav aria-label="Breadcrumb" class="breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/{group_id}/">{group_id}</a></li><li><a href="/{group_id}/{venture.get('id', '')}/" aria-current="page">{name}</a></li></ol></nav>
  <main>
    <header class="hero">
      <h1>{name}</h1>
      <p class="mission">{mission}</p>
    </header>
    <section><h2>Our Offerings</h2><div class="grid">{offerings_html}</div></section>
  </main>
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
