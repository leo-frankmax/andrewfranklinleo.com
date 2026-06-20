# Implementation Phases

5 phases with deliverables, dependencies, and estimated effort.

---

## Phase 1: Foundation & Scaffolding (Week 1-2)

**Goal:** Project structure, conversation parser, base templates.

### Deliverables

| # | Deliverable | Files | Est. Effort |
|---|-------------|-------|-------------|
| 1.1 | Repository setup | `package.json`, `.gitignore`, `README.md` | 0.5 days |
| 1.2 | Conversation parser | `scripts/parse-conversation.js` | 1 day |
| 1.3 | Base templates | `templates/*.html`, `templates/components/*.html` | 2 days |
| 1.4 | Validation scripts | `scripts/validate-structure.js`, `scripts/generate-nav.js` | 1 day |
| 1.5 | ventures.json (seed) | `ventures.json` from conversation parsing | 0.5 days |

### Dependencies
- Node.js v20+ installed on machine
- npm project initialized

### Validation
- `node scripts/parse-conversation.js` produces valid `ventures.json`
- `node scripts/validate-structure.js` passes with 0 errors
- `ventures.json` contains 10 groups, 34+ ventures, 170+ offerings

---

## Phase 2: MCP Servers (Week 2-3)

**Goal:** 5 MCP servers running in Docker containers.

### Deliverables

| # | Deliverable | Files | Est. Effort |
|---|-------------|-------|-------------|
| 2.1 | fs-mcp | `docker/mcp-servers/fs-mcp/*` | 1 day |
| 2.2 | content-mcp | `docker/mcp-servers/content-mcp/*` | 1.5 days |
| 2.3 | template-mcp | `docker/mcp-servers/template-mcp/*` | 1 day |
| 2.4 | graph-mcp | `docker/mcp-servers/graph-mcp/*` | 1.5 days |
| 2.5 | registry-mcp | `docker/mcp-servers/registry-mcp/*` | 1 day |
| 2.6 | Docker Compose | `docker/compose.yml` | 0.5 days |

### Dependencies
- Docker Desktop installed and running
- Python 3.12+ in containers
- OpenAI API key for content-mcp

### Validation
- `docker compose up -d` starts all 5 servers
- Each server responds on its port
- Tools list available via MCP protocol

---

## Phase 3: Agents (Week 3-4)

**Goal:** 5 agents that read ventures.json, create sites, enrich content, build links.

### Deliverables

| # | Deliverable | Files | Est. Effort |
|---|-------------|-------|-------------|
| 3.1 | venture-generator | `docker/agents/venture-generator/*` | 2 days |
| 3.2 | site-creator | `docker/agents/site-creator/*` | 1.5 days |
| 3.3 | content-enricher | `docker/agents/content-enricher/*` | 2 days |
| 3.4 | link-builder | `docker/agents/link-builder/*` | 1.5 days |
| 3.5 | deployer | `docker/agents/deployer/*` | 1 day |

### Dependencies
- Phase 2 (MCP servers) complete
- Base templates from Phase 1

### Validation
- Each agent runs successfully in Docker
- Agent produces expected output files
- Full pipeline: `venture-generator → site-creator → content-enricher → link-builder → deployer` produces `docs/` with all pages

---

## Phase 4: Skills & Plugins (Week 4-5)

**Goal:** 4 skills and 4 plugins for content generation and post-processing.

### Deliverables

| # | Deliverable | Files | Est. Effort |
|---|-------------|-------|-------------|
| 4.1 | biography-generator skill | `docker/skills/biography-generator/*` | 1 day |
| 4.2 | venture-lister skill | `docker/skills/venture-lister/*` | 1 day |
| 4.3 | product-detailer skill | `docker/skills/product-detailer/*` | 1 day |
| 4.4 | landing-page-styler skill | `docker/skills/landing-page-styler/*` | 1 day |
| 4.5 | seo-enhancer plugin | `docker/plugins/seo-enhancer/*` | 1 day |
| 4.6 | analytics-injector plugin | `docker/plugins/analytics-injector/*` | 0.5 days |
| 4.7 | accessibility-auditor plugin | `docker/plugins/accessibility-auditor/*` | 1 day |
| 4.8 | performance-optimizer plugin | `docker/plugins/performance-optimizer/*` | 0.5 days |

### Dependencies
- Phase 3 (agents) complete
- MCP servers from Phase 2

### Validation
- Each skill produces expected output when called via MCP
- Each plugin modifies HTML files correctly
- `sitemap.xml` generated correctly
- `a11y-report.json` shows no critical errors

---

## Phase 5: GitHub Actions & Deployment (Week 5-6)

**Goal:** Self-hosted runner, CI/CD pipeline, GitHub Pages deployment.

### Deliverables

| # | Deliverable | Files | Est. Effort |
|---|-------------|-------|-------------|
| 5.1 | Self-hosted runner setup | Runner config on this machine | 0.5 days |
| 5.2 | GitHub Actions workflow | `.github/workflows/generate-enterprise-sites.yml` | 1 day |
| 5.3 | GitHub Pages config | Repository settings | 0.5 days |
| 5.4 | Environment secrets | API keys, config | 0.5 days |
| 5.5 | End-to-end test | Full pipeline run | 1 day |

### Dependencies
- All previous phases complete
- GitHub repository configured
- GitHub Pages enabled

### Validation
- Runner appears "Online" in GitHub Settings
- Manual workflow dispatch succeeds
- Scheduled run (6 AM daily) executes
- Site deploys to `https://andrewfranklinleo.com`
- `sitemap.xml` lists all pages
- No broken links in generated site

---

## Phase 6: Advanced Features (Week 6+, Optional)

**Goal:** Frankmax One simulation, LIN dashboard, governance portal.

### Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 6.1 | Frankmax One | Unified digital platform simulation |
| 6.2 | LIN Dashboard | Ecosystem metrics visualization |
| 6.3 | Governance Portal | Universal Stewardship Council pages |
| 6.4 | Multi-language | i18n support for global deployment |
| 6.5 | Search | Client-side search across all pages |
| 6.6 | Analytics Dashboard | Public-facing ecosystem metrics |

### Dependencies
- Phase 5 complete
- Site deployed and functional

---

## Timeline Summary

```
Week 1-2:  ████████████ Phase 1 (Foundation)
Week 2-3:  ████████████ Phase 2 (MCP Servers)
Week 3-4:  ████████████ Phase 3 (Agents)
Week 4-5:  ████████████ Phase 4 (Skills & Plugins)
Week 5-6:  ████████████ Phase 5 (GitHub Actions)
Week 6+:   ████████████ Phase 6 (Advanced)
```

**Total core implementation: ~27 working days**

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM API rate limits | Content generation slow | Batch requests, use local fallback model |
| Docker Desktop issues on Windows | Containers won't start | WSL2 backend, fallback to native Node.js |
| GitHub Actions timeout | Pipeline incomplete | Split into smaller jobs, increase timeout |
| ventures.json too large | Slow parsing | Chunk processing, streaming |
| Template conflicts | Broken HTML | Validate before write, rollback on error |
| MCP server crash | Agent fails | Health checks, auto-restart in compose |
