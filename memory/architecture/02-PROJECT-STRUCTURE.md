# Project Structure

## Repository Layout

```
andrewfranklinleo.com/
│
├── .github/
│   └── workflows/
│       └── generate-enterprise-sites.yml     # Main CI/CD pipeline
│
├── docker/
│   ├── compose.yml                           # Orchestrates all containers
│   │
│   ├── agents/
│   │   ├── venture-generator/                # Reads ventures.json → expands
│   │   │   ├── Dockerfile
│   │   │   ├── agent.py
│   │   │   ├── prompt.md
│   │   │   └── requirements.txt
│   │   │
│   │   ├── site-creator/                     # Creates dirs + index.html
│   │   │   ├── Dockerfile
│   │   │   ├── agent.py
│   │   │   ├── prompt.md
│   │   │   └── requirements.txt
│   │   │
│   │   ├── content-enricher/                 # Fills in offering pages
│   │   │   ├── Dockerfile
│   │   │   ├── agent.py
│   │   │   ├── prompt.md
│   │   │   └── requirements.txt
│   │   │
│   │   ├── link-builder/                     # Cross-links related nodes
│   │   │   ├── Dockerfile
│   │   │   ├── agent.py
│   │   │   ├── prompt.md
│   │   │   └── requirements.txt
│   │   │
│   │   └── deployer/                         # Builds static site
│   │       ├── Dockerfile
│   │       ├── agent.py
│   │       ├── prompt.md
│   │       └── requirements.txt
│   │
│   ├── mcp-servers/
│   │   ├── fs-mcp/                           # File system operations
│   │   │   ├── Dockerfile
│   │   │   ├── server.py
│   │   │   └── requirements.txt
│   │   │
│   │   ├── content-mcp/                      # LLM content generation
│   │   │   ├── Dockerfile
│   │   │   ├── server.py
│   │   │   ├── config.yaml
│   │   │   └── requirements.txt
│   │   │
│   │   ├── template-mcp/                     # HTML template management
│   │   │   ├── Dockerfile
│   │   │   ├── server.py
│   │   │   └── requirements.txt
│   │   │
│   │   ├── graph-mcp/                        # Site graph & relationships
│   │   │   ├── Dockerfile
│   │   │   ├── server.py
│   │   │   └── requirements.txt
│   │   │
│   │   └── registry-mcp/                     # Plugin/skill registry
│   │       ├── Dockerfile
│   │       ├── server.py
│   │       └── requirements.txt
│   │
│   ├── plugins/
│   │   ├── seo-enhancer/
│   │   │   ├── Dockerfile
│   │   │   ├── plugin.py
│   │   │   └── requirements.txt
│   │   │
│   │   ├── analytics-injector/
│   │   │   ├── Dockerfile
│   │   │   ├── plugin.py
│   │   │   └── requirements.txt
│   │   │
│   │   ├── accessibility-auditor/
│   │   │   ├── Dockerfile
│   │   │   ├── plugin.py
│   │   │   └── requirements.txt
│   │   │
│   │   └── performance-optimizer/
│   │       ├── Dockerfile
│   │       ├── plugin.py
│   │       └── requirements.txt
│   │
│   └── skills/
│       ├── biography-generator/
│       ├── venture-lister/
│       ├── product-detailer/
│       └── landing-page-styler/
│
├── scripts/
│   ├── parse-conversation.js                 # Extract ventures.json from markdown
│   ├── validate-structure.js                 # Verify site tree integrity
│   └── generate-nav.js                       # Build global navigation
│
├── templates/
│   ├── base.html                             # Global layout shell
│   ├── group-landing.html                    # Group page (Frankmax, etc.)
│   ├── venture-landing.html                  # Venture page (Frankmax Talent, etc.)
│   ├── offering-landing.html                 # Product/Service page
│   ├── conglomerate-home.html                # Leo Global Holdings portal
│   └── components/
│       ├── nav.html                          # Global navigation
│       ├── footer.html                       # Global footer
│       ├── breadcrumb.html                   # Breadcrumb trail
│       ├── card.html                         # Venture/offering card
│       ├── sidebar.html                      # Left sidebar nav
│       └── hero.html                         # Hero banner
│
├── sites/                                    # SOURCE CONTENT (git-tracked)
│   └── leo-global-holdings/
│       ├── index.html                        # Conglomerate portal
│       ├── _conglomerate.json                # Conglomerate metadata
│       │
│       ├── frankmax/                         # Group
│       │   ├── index.html
│       │   ├── _group.json
│       │   │
│       │   ├── frankmax-talent/              # Venture
│       │   │   ├── index.html
│       │   │   ├── _venture.json
│       │   │   ├── executive-search/         # Offering
│       │   │   │   ├── index.html
│       │   │   │   └── _offering.json
│       │   │   ├── workforce-management/
│       │   │   │   ├── index.html
│       │   │   │   └── _offering.json
│       │   │   └── career-development/
│       │   │       ├── index.html
│       │   │       └── _offering.json
│       │   │
│       │   ├── frankmax-learning/
│       │   ├── frankmax-consulting/
│       │   ├── frankmax-digital/
│       │   ├── frankmax-leadership/
│       │   ├── frankmax-research/
│       │   └── frankmax-workforce-solutions/
│       │
│       ├── virginbay/
│       ├── glosbe/
│       ├── crenza/
│       ├── leo-technologies/
│       ├── leo-capital/
│       ├── leo-ventures/
│       ├── leo-institute/
│       ├── leo-foundation/
│       └── leo-global-governance-council/
│
├── docs/                                     # BUILT OUTPUT (GitHub Pages)
│   ├── index.html
│   ├── sitemap.xml
│   └── ... (all generated pages)
│
├── memory/                                   # Architecture docs & conversation
│   ├── chatgpt-conversation-andrew-franklin-leo.md
│   ├── architecture/
│   └── tasks.md
│
├── package.json                              # Node.js dependencies
├── .gitignore
└── README.md
```

## Key Directories

| Directory | Purpose | Tracked in Git |
|-----------|---------|----------------|
| `sites/` | Source content with metadata | Yes (source of truth) |
| `docs/` | Built static output | Yes (deployed to GitHub Pages) |
| `templates/` | HTML templates | Yes |
| `docker/` | Container definitions | Yes |
| `scripts/` | Build scripts | Yes |
| `memory/` | Architecture docs | Yes |

## Metadata Files

Every node in the site tree has a JSON metadata file:

| Level | File | Contents |
|-------|------|----------|
| Conglomerate | `_conglomerate.json` | Name, mission, groups[], settings |
| Group | `_group.json` | Name, mission, ventures[], parent |
| Venture | `_venture.json` | Name, mission, offerings[], industry, type, parent |
| Offering | `_offering.json` | Name, functions[], output, customers[], parent |
