# Open Decisions

Questions that need your input before implementation begins.

---

## Decision 1: LLM Provider

**Question:** Which LLM to use for content generation?

| Option | Pros | Cons |
|--------|------|------|
| **OpenAI API (GPT-4.1)** | High quality, fast, reliable | Costs money per token, data sent to cloud |
| **Anthropic API (Claude)** | High quality, long context | Costs money, API keys needed |
| **Local (Ollama/LM Studio)** | Free, private, no API key | Slower, lower quality, needs GPU |
| **Hybrid** | Local for drafts, cloud for polish | More complex setup |

**Recommendation:** Hybrid — Local (Ollama) for initial drafts, OpenAI for final polish.

**Status:** Pending your decision.

---

## Decision 2: Static Site Hosting

**Question:** Where to deploy the generated site?

| Option | Pros | Cons |
|--------|------|------|
| **GitHub Pages** | Free, integrates with Actions, custom domain | Static only, 100GB bandwidth/month |
| **Netlify** | Free tier, forms, functions, CDN | 100GB bandwidth/month, build minutes |
| **Vercel** | Fast, Edge functions, great DX | 100GB bandwidth/month, serverless limits |
| **Custom VPS** | Full control, unlimited | Costs money, needs management |

**Recommendation:** GitHub Pages (free, already in pipeline, custom domain support).

**Status:** Pending your decision.

---

## Decision 3: Theme & Styling

**Question:** Which CSS framework for consistent styling?

| Option | Pros | Cons |
|--------|------|------|
| **Tailwind CSS** | Utility-first, consistent, fast to iterate | Large initial setup, many classes |
| **Bootstrap 5** | Familiar, many components, grid system | Generic look, larger bundle |
| **Custom CSS** | Full control, unique look | More work, harder to maintain |
| **Pico CSS** | Minimal, classless, semantic | Limited customization |

**Recommendation:** Tailwind CSS — rapid iteration, consistent design, easy to template.

**Status:** Pending your decision.

---

## Decision 4: State Persistence

**Question:** How to store site graph and metadata?

| Option | Pros | Cons |
|--------|------|------|
| **File-based (JSON)** | Simple, git-trackable, matches SharePoint analogy | No queries, large files |
| **SQLite** | Fast queries, single file | Needs library, not git-friendly |
| **Redis** | Fast, in-memory | Needs server, not persistent |

**Recommendation:** File-based JSON — matches SharePoint content database analogy, keeps it simple, git-trackable.

**Status:** Pending your decision.

---

## Decision 5: Runner OS

**Question:** How to run the self-hosted GitHub Actions runner?

| Option | Pros | Cons |
|--------|------|------|
| **Windows (native)** | Already on this machine, PowerShell scripts | Slower Docker, larger images |
| **WSL2/Ubuntu** | Faster Docker, Linux-native | Needs WSL2 setup, dual filesystem |
| **Docker Desktop Linux** | Native Docker, isolated | Requires Docker Desktop |

**Recommendation:** Windows runner with Docker Desktop Linux containers — least setup, already available.

**Status:** Pending your decision.

---

## Decision 6: Initial Scope

**Question:** Build all 34+ ventures at once, or iterate?

| Option | Pros | Cons |
|--------|------|------|
| **All at once** | Complete site from day 1 | Longer initial build, harder to debug |
| **Iterative (Frankmax first)** | Faster feedback, easier debugging | Partial site for first few weeks |
| **Incremental (1 group/week)** | Balanced approach | Needs careful coordination |

**Recommendation:** Iterative — Frankmax Group first (7 ventures, 35+ offerings), then expand weekly.

**Status:** Pending your decision.

---

## Decision 7: Content Quality

**Question:** How much LLM-generated content vs. manual content?

| Option | Pros | Cons |
|--------|------|------|
| **Full LLM generation** | Automated, scalable | May need editing, inconsistent quality |
| **LLM drafts + manual polish** | Better quality, human touch | More manual work |
| **Manual only** | Highest quality | Doesn't scale, defeats automation purpose |

**Recommendation:** LLM drafts + manual polish — agents generate first drafts, you review and refine.

**Status:** Pending your decision.

---

## Decision 8: Multi-tenancy

**Question:** Should each group have its own subdomain or stay under one domain?

| Option | Example | Pros | Cons |
|--------|---------|------|------|
| **Single domain** | `andrewfranklinleo.com/frankmax/` | Simple, unified | Long URLs |
| **Subdomains** | `frankmax.andrewfranklinleo.com` | Clean URLs, separate branding | DNS complexity |
| **Path-based** | `andrewfranklinleo.com/g/frankmax/` | Clean, organized | Still under one domain |

**Recommendation:** Path-based — `andrewfranklinleo.com/frankmax/talent/executive-search/`

**Status:** Pending your decision.

---

## Summary Table

| # | Decision | Recommendation | Your Call? |
|---|----------|---------------|------------|
| 1 | LLM Provider | Hybrid (Local + OpenAI) | Pending |
| 2 | Hosting | GitHub Pages | Pending |
| 3 | Styling | Tailwind CSS | Pending |
| 4 | State | File-based JSON | Pending |
| 5 | Runner | Windows + Docker Desktop | Pending |
| 6 | Scope | Iterative (Frankmax first) | Pending |
| 7 | Content | LLM drafts + manual polish | Pending |
| 8 | Multi-tenancy | Path-based URLs | Pending |
