# Architecture Overview

## What We're Building

A **self-generating, AI-driven HTML-based CMS** that mirrors SharePoint's hierarchy but runs as a static-site generator. It reads the Andrew Franklin Leo conceptual blueprint, generates venture portfolios, and creates dedicated landing pages for every venture, product, service, solution, and offering — all automatically via Docker agents, MCP servers, and GitHub Actions.

## SharePoint Analogy

| SharePoint Concept | System Mapping | Example |
|---|---|---|
| Web Application | **Conglomerate** | Leo Global Holdings |
| Site Collection | **Group** | Frankmax Group |
| Site | **Venture** | Frankmax Talent |
| Sub-site | **Product/Service/Solution/Offering** | Executive Search |
| Web Part / Component | **Packaged capability** | Search widget, career planner |
| Content Database | **File system + JSON metadata** | `sites/{group}/{venture}/_venture.json` |

## Key Principles

1. **Static-first**: All output is pure HTML — no server-side rendering, no database
2. **Self-reinforcing**: Each run proposes new ventures → next run detects gaps → fills them
3. **AI-powered**: Agents use LLMs via MCP to generate rich content
4. **Docker-orchestrated**: Every component runs in its own container
5. **GitHub Actions**: Self-hosted runner on this machine triggers the full pipeline

## Source Data

The ChatGPT conversation file (`memory/chatgpt-conversation-andrew-franklin-leo.md`) contains 16 turns of structured content:

| Turn | Content | Usage |
|------|---------|-------|
| 2 | Four pillars identified | Foundation: Frankmax, Virginbay, Glosbe, Crenza |
| 4 | Full biography | Landing page content, founder story |
| 6 | Leadership philosophy | Governance framework, Leader's Oath |
| 8 | Business empire structure | Full hierarchy: Leo Global Holdings + 9 entities |
| 10 | Timeline (1995–2060) | Historical context, milestone pages |
| 12 | Global mission & vision | Vision/mission pages, Seven Commitments |
| 14 | Detailed corporate ecosystem | Division-level detail for all four groups |
| 16 | Master prompt for ventures | AI agent template for generating new ventures |

## Architecture Layers

```
┌─────────────────────────────────────────────┐
│           GitHub Actions Workflow            │
│  (self-hosted runner on this Windows machine)│
├─────────────────────────────────────────────┤
│              Docker Orchestrator              │
├──────┬──────┬──────┬──────┬──────┬──────────┤
│Agent │Agent │Agent │Agent │Agent │ Plugins  │
│Vent- │Site- │Cont- │Link- │Depl- │  & Skills│
│Gen   │Crt   │Enrch │Build │oyr   │          │
├──────┴──────┴──────┴──────┴──────┴──────────┤
│              MCP Servers (5)                  │
│  fs │ content │ template │ graph │ registry  │
├─────────────────────────────────────────────┤
│            Content Sources                    │
│  ventures.json │ templates/ │ sites/          │
└─────────────────────────────────────────────┘
```

## Related Documents

- [01-VENTURE-HIERARCHY.md](./01-VENTURE-HIERARCHY.md) — Complete tree
- [02-PROJECT-STRUCTURE.md](./02-PROJECT-STRUCTURE.md) — File/folder layout
- [03-MCP-SERVERS.md](./03-MCP-SERVERS.md) — Server specifications
- [04-AGENTS.md](./04-AGENTS.md) — Agent specifications
- [05-SKILLS.md](./05-SKILLS.md) — Skill definitions
- [06-PLUGINS.md](./06-PLUGINS.md) — Plugin specifications
- [07-GITHUB-ACTIONS.md](./07-GITHUB-ACTIONS.md) — CI/CD pipeline
- [08-SITE-STRUCTURE.md](./08-SITE-STRUCTURE.md) — SharePoint mapping
- [09-PHASES.md](./09-PHASES.md) — Implementation phases
- [10-DECISIONS.md](./10-DECISIONS.md) — Open questions
