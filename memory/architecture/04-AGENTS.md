# Agents

5 autonomous workers running in Docker containers. Each agent reads the venture tree, detects gaps, generates content, and creates pages. They communicate via the filesystem and MCP servers.

## Agent List

| Agent | Docker Image | Trigger | Inputs | Outputs |
|-------|-------------|---------|--------|---------|
| `venture-generator` | `agents/venture-generator` | Workflow start | `ventures.json`, conversation file | Updated `ventures.json` |
| `site-creator` | `agents/site-creator` | After venture-gen | `ventures.json` | Directory structure + `index.html` files |
| `content-enricher` | `agents/content-enricher` | After site-creator | Site tree + `_venture.json` | Filled offering pages |
| `link-builder` | `agents/link-builder` | After content-enricher | All `_*.json` files | Cross-links, nav, related |
| `deployer` | `agents/deployer` | Last | All `sites/` content | `docs/` built output |

---

## Agent 1: venture-generator

**Purpose:** Read the source data, apply the master prompt, generate/expand the venture tree.

### Logic

1. Read `ventures.json` (seed data from conversation parser)
2. Read conversation file for context (Turn 8 hierarchy + Turn 14 detail)
3. For each Group that needs expansion:
   - Apply master prompt (Turn 16) via `content-mcp`
   - Generate new ventures covering all economic sectors
   - Classify as: core, strategic, emerging, support, social
4. Add ecosystem relationships (upstream/downstream flows)
5. Write updated `ventures.json`
6. Write individual `_venture.json` files for new ventures

### MCP Tools Used
- `content-mcp.expand_venture_list(group, master_prompt)`
- `content-mcp.generate_venture_description(venture_data)`
- `graph-mcp.add_node(path, metadata)`
- `graph-mcp.find_gaps()`
- `fs-mcp.read_json(ventures.json)`
- `fs-mcp.write_json(ventures.json, data)`

### Output Format (`ventures.json`)

```json
{
  "version": "2.0",
  "last_updated": "2026-06-19T00:00:00Z",
  "groups": [
    {
      "id": "frankmax",
      "name": "Frankmax Group",
      "mission": "Empowering Every Professional",
      "ventures": [
        {
          "id": "frankmax-talent",
          "name": "Frankmax Talent",
          "mission": "Recruit and develop world-class professionals",
          "industry": "Human Resources",
          "type": "core",
          "offerings": [
            {
              "id": "executive-search",
              "name": "Executive Search",
              "functions": ["C-suite recruitment", "Board placement", "Senior leadership"],
              "output": "Qualified executives enter the ecosystem",
              "customers": ["Enterprises", "Boards of Directors"]
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Agent 2: site-creator

**Purpose:** Create directory structure and generate landing pages for every node.

### Logic

1. Read `ventures.json`
2. For each Group → Venture → Offering:
   - Create directory under `sites/leo-global-holdings/{group}/{venture}/{offering}/`
   - Generate `_group.json`, `_venture.json`, `_offering.json` metadata
   - Render `index.html` from appropriate template
   - Inject: name, mission, breadcrumbs, nav, parent/child links
3. Create `global-nav.json` at root
4. Create conglomerate portal `index.html`

### MCP Tools Used
- `fs-mcp.create_directory(path)`
- `fs-mcp.write_file(path, content)`
- `fs-mcp.write_json(path, data)`
- `template-mcp.render_template(template, vars)`
- `graph-mcp.build_global_nav()`
- `graph-mcp.get_children(path)`

### Template Mapping

| Node Type | Template | Variables |
|-----------|----------|-----------|
| Conglomerate | `conglomerate-home.html` | groups[], mission, vision |
| Group | `group-landing.html` | group, ventures[], mission |
| Venture | `venture-landing.html` | venture, offerings[], mission |
| Offering | `offering-landing.html` | offering, functions[], output |

---

## Agent 3: content-enricher

**Purpose:** Fill in detailed content for offering pages (products, services, solutions).

### Logic

1. Read all `_offering.json` files in site tree
2. For each offering:
   - Check if `index.html` has placeholder content
   - Generate detailed content via `content-mcp`:
     - Full description
     - Features list
     - Benefits
     - Use cases
     - Target audience
     - Revenue model
     - Related offerings (via `graph-mcp`)
   - Update `index.html` with enriched content
3. For each venture:
   - Ensure all offerings are documented
   - Fill in missing metadata
   - Add cross-references to related ventures

### MCP Tools Used
- `content-mcp.generate_offering_description(offering_data)`
- `content-mcp.generate_seo_meta(page_data)`
- `template-mcp.render_template(offering-landing.html, enriched_vars)`
- `fs-mcp.read_file(index.html)`
- `fs-mcp.write_file(index.html, enriched_html)`
- `graph-mcp.get_related(path)`

---

## Agent 4: link-builder

**Purpose:** Build cross-references, update navigation, create related-venture links.

### Logic

1. Read all `_*.json` files from site tree
2. Build complete graph via `graph-mcp`
3. For each node:
   - Add `related` array to metadata (ventures in same group + cross-group)
   - Add `ecosystem_flows` (upstream/downstream)
   - Inject related-venture cards into `index.html`
4. Update `global-nav.json` with complete tree
5. Update breadcrumb components
6. Generate cross-link sections for each page
7. Validate: no orphan pages, all links resolve

### MCP Tools Used
- `graph-mcp.get_node(path)`
- `graph-mcp.get_siblings(path)`
- `graph-mcp.get_related(path)`
- `graph-mcp.get_ecosystem_flows()`
- `graph-mcp.update_node(path, metadata)`
- `graph-mcp.validate_graph()`
- `fs-mcp.write_json(global-nav.json, nav_data)`
- `fs-mcp.write_json(_venture.json, updated_metadata)`

### Cross-Link Rules

| Source | Target | Reason |
|--------|--------|--------|
| Frankmax Talent | Virginbay Services | Talent flows to commerce |
| Virginbay Marketplace | Glosbe Communities | Commerce builds communities |
| Glosbe Communities | Crenza Wealth | Communities create assets |
| Crenza Investments | Leo Ventures | Capital funds innovation |
| Any venture | Same-group siblings | Navigation |
| Any venture | Cross-ecosystem flows | Business logic |

---

## Agent 5: deployer

**Purpose:** Build final static site, optimize assets, prepare for deployment.

### Logic

1. Read complete site tree from `sites/`
2. Copy all HTML, CSS, JS, assets to `docs/`
3. Generate `sitemap.xml`
4. Generate `robots.txt`
5. Copy `global-nav.json` for client-side use
6. Optimize HTML (minify, remove comments)
7. Validate all links resolve
8. Generate deployment manifest

### MCP Tools Used
- `fs-mcp.read_file(path)`
- `fs-mcp.write_file(path, content)`
- `fs-mcp.list_directory(path)`
- `template-mcp.validate_html(html)`

### Output

```
docs/
├── index.html                              # Conglomerate portal
├── sitemap.xml
├── robots.txt
├── global-nav.json
├── frankmax/
│   ├── index.html                          # Group landing
│   ├── frankmax-talent/
│   │   ├── index.html                      # Venture landing
│   │   ├── executive-search/
│   │   │   └── index.html                  # Offering page
│   │   └── ...
│   └── ...
├── virginbay/
├── glosbe/
├── crenza/
└── ... (all generated pages)
```

---

## Agent Communication Pattern

```
venture-generator
    │
    ▼
ventures.json (updated)
    │
    ▼
site-creator
    │
    ▼
sites/leo-global-holdings/{all nodes created}
    │
    ▼
content-enricher
    │
    ▼
sites/leo-global-holdings/{all pages enriched}
    │
    ▼
link-builder
    │
    ▼
sites/leo-global-holdings/{all cross-links added}
    │
    ▼
deployer
    │
    ▼
docs/ (built static site)
```

## Error Handling

| Scenario | Action |
|----------|--------|
| MCP server unreachable | Retry 3x, then skip with warning |
| LLM timeout | Use placeholder content, log for next run |
| File write permission denied | Log error, skip file |
| Invalid HTML | Log warning, continue |
| Graph validation fails | Log errors, attempt auto-fix |
