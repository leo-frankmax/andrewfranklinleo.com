# Self-Hosted Runner Setup Guide

## Prerequisites

- Windows 10/11 with admin access
- Docker Desktop installed and running
- Node.js 20+ installed
- Python 3.12+ installed

## Steps

### 1. Generate Runner Token

1. Go to: https://github.com/andrewfranklinleo/andrewfranklinleo.com/settings/actions/runners
2. Click **"New self-hosted runner"**
3. Select **Windows** as the platform
4. Copy the token from the setup command (the `--token` value)

### 2. Run Setup Script

Open PowerShell as Administrator and run:

```powershell
cd "C:\Users\Andrew Franklin Leo\Documents\Projects\andrewfranklinleo.com"
powershell -ExecutionPolicy Bypass -File ".github/scripts/setup-runner.ps1" -Token "YOUR_TOKEN_HERE"
```

Replace `YOUR_TOKEN_HERE` with the token from step 1.

### 3. Verify Runner

After setup, the runner should appear in GitHub:
- Go to: https://github.com/andrewfranklinleo/andrewfranklinleo.com/settings/actions/runners
- You should see the runner with a green dot (online)

### 4. Test the Pipeline

Trigger a manual run:
- Go to: https://github.com/andrewfranklinleo/andrewfranklinleo.com/actions/workflows/generate-enterprise-sites.yml
- Click **"Run workflow"**
- Select **main** branch
- Click **"Run workflow"**

## Troubleshooting

### Runner not connecting
- Check Docker Desktop is running
- Check Node.js and Python are in PATH
- Check firewall allows outbound HTTPS to github.com

### Pipeline fails on tests
- Run locally first: `.\.github\scripts\run-pipeline.ps1`
- Check Docker images build: `docker compose -f docker/compose.yml build`

### Pipeline fails on agents
- Check MCP servers start: `docker compose -f docker/compose.yml up -d`
- Check ports 3001-3005 are available
