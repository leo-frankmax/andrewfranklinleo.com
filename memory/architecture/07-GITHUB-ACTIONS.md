# GitHub Actions & Self-Hosted Runner

## Self-Hosted Runner Setup

### Machine Requirements

| Requirement | Specification |
|-------------|---------------|
| OS | Windows 10/11 (this machine) |
| Path | `C:\Users\Andrew Franklin Leo` |
| Docker Desktop | Installed, running Linux containers |
| Node.js | v20+ |
| GitHub CLI | `gh` installed |
| Disk | 50GB+ free space |

### Runner Registration

```powershell
# 1. Go to GitHub repo → Settings → Actions → Runners → New self-hosted runner

# 2. Download and configure (replace USER/TOKEN)
cd C:\Users\Andrew Franklin Leo\actions-runner
.\config.cmd --url https://github.com/USER/andrewfranklinleo.com --token XXXXXXXXXXXXXXXXX

# 3. Install as Windows service
.\svc.cmd install

# 4. Start the service
.\svc.cmd start

# 5. Verify in GitHub Settings → Actions → Runners → "Online"
```

### Runner Labels

| Label | Purpose |
|-------|---------|
| `self-hosted` | Default label for this runner |
| `windows` | Windows-specific jobs |
| `docker` | Jobs requiring Docker |

---

## Workflow Definition

**File:** `.github/workflows/generate-enterprise-sites.yml`

```yaml
name: Generate Enterprise Sites

on:
  workflow_dispatch:
    inputs:
      force_full_regen:
        description: 'Force full regeneration (ignore cache)'
        type: boolean
        default: false
      target_group:
        description: 'Target specific group (leave empty for all)'
        type: choice
        options:
          - ''
          - frankmax
          - virginbay
          - glosbe
          - crenza
          - all
        default: ''

  schedule:
    - cron: '0 6 * * *'  # Daily at 6:00 AM UTC

  push:
    paths:
      - 'memory/chatgpt-conversation-andrew-franklin-leo.md'
      - 'scripts/**'
      - 'templates/**'
      - 'docker/**'
    branches:
      - main

env:
  NODE_VERSION: '20'
  DOCKER_COMPOSE_FILE: 'docker/compose.yml'

jobs:
  parse:
    name: Parse Conversation
    runs-on: self-hosted
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Install dependencies
        run: npm ci

      - name: Parse conversation → ventures.json
        run: node scripts/parse-conversation.js

      - name: Upload ventures.json
        uses: actions/upload-artifact@v4
        with:
          name: ventures
          path: ventures.json
          retention-days: 1

  generate:
    name: Generate Sites
    runs-on: self-hosted
    timeout-minutes: 60
    needs: parse
    steps:
      - uses: actions/checkout@v4

      - name: Download ventures.json
        uses: actions/download-artifact@v4
        with:
          name: ventures

      - name: Setup Docker
        uses: docker/setup-buildx-action@v3

      - name: Start MCP servers
        run: docker compose -f ${{ env.DOCKER_COMPOSE_FILE }} up -d mcp-servers
        working-directory: .

      - name: Wait for MCP servers
        run: |
          Write-Host "Waiting for MCP servers to start..."
          Start-Sleep -Seconds 10
          # Health check
          $servers = @("fs-mcp", "content-mcp", "template-mcp", "graph-mcp", "registry-mcp")
          foreach ($server in $servers) {
            Write-Host "Checking $server..."
          }

      - name: Run venture-generator agent
        run: |
          docker run --rm --network host `
            -v "${{ github.workspace }}:/data" `
            -e TARGET_GROUP="${{ inputs.target_group || 'all' }}" `
            -e FORCE_REGEN="${{ inputs.force_full_regen || 'false' }}" `
            agents/venture-generator

      - name: Run site-creator agent
        run: |
          docker run --rm --network host `
            -v "${{ github.workspace }}:/data" `
            agents/site-creator

      - name: Run content-enricher agent
        run: |
          docker run --rm --network host `
            -v "${{ github.workspace }}:/data" `
            agents/content-enricher

      - name: Run link-builder agent
        run: |
          docker run --rm --network host `
            -v "${{ github.workspace }}:/data" `
            agents/link-builder

      - name: Run deployer agent
        run: |
          docker run --rm --network host `
            -v "${{ github.workspace }}:/data" `
            agents/deployer

      - name: Stop MCP servers
        if: always()
        run: docker compose -f ${{ env.DOCKER_COMPOSE_FILE }} down

  post-process:
    name: Post-Process (Plugins)
    runs-on: self-hosted
    timeout-minutes: 30
    needs: generate
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run SEO enhancer
        run: |
          docker run --rm `
            -v "${{ github.workspace }}/docs:/data/docs" `
            plugins/seo-enhancer

      - name: Run analytics injector
        run: |
          docker run --rm `
            -v "${{ github.workspace }}/docs:/data/docs" `
            plugins/analytics-injector

      - name: Run accessibility auditor
        run: |
          docker run --rm `
            -v "${{ github.workspace }}/docs:/data/docs" `
            plugins/accessibility-auditor

      - name: Run performance optimizer
        run: |
          docker run --rm `
            -v "${{ github.workspace }}/docs:/data/docs" `
            plugins/performance-optimizer

      - name: Upload deployment artifact
        uses: actions/upload-artifact@v4
        with:
          name: built-site
          path: docs/
          retention-days: 7

  deploy:
    name: Deploy to GitHub Pages
    runs-on: self-hosted
    timeout-minutes: 10
    needs: post-process
    if: github.ref == 'refs/heads/main'
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Download built site
        uses: actions/download-artifact@v4
        with:
          name: built-site
          path: docs/

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4

  commit-generated:
    name: Commit Generated Content
    runs-on: self-hosted
    timeout-minutes: 10
    needs: post-process
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Download built site
        uses: actions/download-artifact@v4
        with:
          name: built-site
          path: docs/

      - name: Configure git
        run: |
          git config user.name "afl-bot"
          git config user.email "bot@andrewfranklinleo.com"

      - name: Commit and push
        run: |
          git add docs/ sites/
          if ! git diff --cached --quiet; then
            git commit -m "auto: regenerate enterprise sites [skip ci]"
            git push
          } else {
            Write-Host "No changes to commit"
          }
```

---

## Workflow Triggers

| Trigger | When | What Runs |
|---------|------|-----------|
| `workflow_dispatch` | Manual from GitHub UI | Full pipeline |
| `schedule` | Daily 6 AM UTC | Full pipeline |
| `push` (paths) | Code/templates change | Full pipeline |
| `push` (main) | Deploy | Includes deploy job |

---

## Environment Variables

| Variable | Source | Purpose |
|----------|--------|---------|
| `OPENAI_API_KEY` | GitHub Secrets | LLM API access |
| `GITHUB_TOKEN` | Automatic | GitHub API, Pages deploy |
| `GA_MEASUREMENT_ID` | GitHub Secrets | Google Analytics |

---

## Caching Strategy

| What | Where | TTL |
|------|-------|-----|
| MCP server images | Docker layer cache | Until Dockerfile changes |
| Node modules | `actions/cache` | Until package-lock.json changes |
| ventures.json | Artifact | 1 run |
| Built site | Artifact | 7 days |
| Generated HTML | Git commit | Permanent |

---

## Monitoring

| Check | Method |
|-------|--------|
| Runner health | `http://localhost:8080` (runner status) |
| MCP servers | Health check endpoint on each port |
| Workflow status | GitHub Actions UI |
| Site uptime | GitHub Pages status |
| Generated pages | `sitemap.xml` count vs expected |
