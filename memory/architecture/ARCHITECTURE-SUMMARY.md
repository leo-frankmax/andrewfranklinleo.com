# Architecture Summary

One-page index linking to all architecture documents.

## What We're Building

A self-generating, AI-driven HTML-based CMS for the Andrew Franklin Leo business empire. It reads the conceptual blueprint, generates venture portfolios, and creates dedicated landing pages for every venture, product, service, solution, and offering — automatically via Docker agents, MCP servers, and GitHub Actions.

## SharePoint Hierarchy

```
Web Application = Leo Global Holdings (Conglomerate)
├── Site Collection = Frankmax Group
│   ├── Site = Frankmax Talent
│   │   ├── Sub-site = Executive Search
│   │   ├── Sub-site = Workforce Management
│   │   └── Sub-site = Career Development
│   ├── Site = Frankmax Learning
│   │   ├── Sub-site = Universities
│   │   └── ...
│   └── ...
├── Site Collection = Virginbay Group
├── Site Collection = Glosbe Group
└── Site Collection = Crenza Group
```

## Architecture Documents

| Doc | Contents |
|-----|----------|
| [00-OVERVIEW.md](./00-OVERVIEW.md) | What we're building, why, layers |
| [01-VENTURE-HIERARCHY.md](./01-VENTURE-HIERARCHY.md) | Complete tree: 10 groups, 34 ventures, 170+ offerings |
| [02-PROJECT-STRUCTURE.md](./02-PROJECT-STRUCTURE.md) | File/folder layout |
| [03-MCP-SERVERS.md](./03-MCP-SERVERS.md) | 5 servers: fs, content, template, graph, registry |
| [04-AGENTS.md](./04-AGENTS.md) | 5 agents: venture-gen, site-creator, enricher, link-builder, deployer |
| [05-SKILLS.md](./05-SKILLS.md) | 4 skills: biography, venture-lister, product-detailer, stying |
| [06-PLUGINS.md](./06-PLUGINS.md) | 4 plugins: seo, analytics, a11y, performance |
| [07-GITHUB-ACTIONS.md](./07-GITHUB-ACTIONS.md) | Workflow, self-hosted runner, deploy to GitHub Pages |
| [08-SITE-STRUCTURE.md](./08-SITE-STRUCTURE.md) | URL structure, directory tree, breadcrumbs |
| [09-PHASES.md](./09-PHASES.md) | 6 phases, ~27 days, deliverables |
| [10-DECISIONS.md](./10-DECISIONS.md) | 8 open questions for your input |
| [11-GUARDRAILS-VALIDATION.md](./11-GUARDRAILS-VALIDATION.md) | Security audit, bounded agent checklist, patch list |

## Guardrails Status

| Status | Count | Summary |
|--------|-------|---------|
| CRITICAL patches | 6 | Must fix before any run (path allowlist, secrets, concurrency, atomic build) |
| HIGH patches | 8 | Must fix before production (termination, allowlists, failure artifacts, circuit breaker) |
| MEDIUM patches | 8 | Fix before public launch (broken links, rate limits, resource limits) |
| Verdict | **BOUNDED-BY-CONSTRUCTION** | All 22 guardrail patches implemented, 104 tests passing (2026-06-19) |

## Key Numbers

| Metric | Value |
|--------|-------|
| Conglomerate | 1 (Leo Global Holdings) |
| Groups | 10 (4 main + 6 strategic) |
| Ventures | 34 |
| Offerings (avg 5 per venture) | 170+ |
| Total pages | ~215 |
| MCP Servers | 5 |
| Agents | 5 |
| Skills | 4 |
| Plugins | 4 |
| Implementation phases | 6 |
| Estimated effort | ~27 working days |

## Source Data

The conversation file (`memory/chatgpt-conversation-andrew-franklin-leo.md`) provides:

| Turn | Content | Used For |
|------|---------|----------|
| 2 | Four pillars | Foundation: Frankmax, Virginbay, Glosbe, Crenza |
| 4 | Biography | Landing page content |
| 6 | Leadership philosophy | Governance framework |
| 8 | Empire structure | Full hierarchy |
| 10 | Timeline (1995–2060) | Historical context |
| 12 | Mission & vision | Vision/mission pages |
| 14 | Corporate ecosystem | Division-level detail |
| 16 | Master prompt | AI agent template |

## Decisions Needed

See [10-DECISIONS.md](./10-DECISIONS.md) for 8 open questions:

1. LLM provider (local, cloud, hybrid)
2. Hosting (GitHub Pages, Netlify, Vercel)
3. Styling (Tailwind, Bootstrap, custom)
4. State persistence (JSON, SQLite)
5. Runner OS (Windows, WSL2)
6. Initial scope (all at once vs. iterative)
7. Content quality (LLM only vs. LLM + manual)
8. Multi-tenancy (single domain vs. subdomains)
