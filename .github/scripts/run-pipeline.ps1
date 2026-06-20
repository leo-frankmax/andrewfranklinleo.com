#!/usr/bin/env pwsh
# Pipeline Orchestration Script
# Runs the full agent pipeline locally (outside Docker).
# Usage: .\run-pipeline.ps1 [-TargetGroup all] [-ForceRegen $false] [-SkipTests]

param(
    [string]$TargetGroup = "all",
    [bool]$ForceRegen = $false,
    [switch]$SkipTests,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot | Split-Path -Parent | Split-Path -Parent
$env:PYTHONPATH = Join-Path $projectRoot "docker"

Write-Host "=== Andrew Franklin Leo CMS - Pipeline ===" -ForegroundColor Cyan
Write-Host "Target Group: $TargetGroup" -ForegroundColor Yellow
Write-Host "Force Regen: $ForceRegen" -ForegroundColor Yellow

# Step 1: Run tests
if (-not $SkipTests) {
    Write-Host "`n[1/8] Running TypeScript tests..." -ForegroundColor Green
    Push-Location $projectRoot
    npx vitest run
    if ($LASTEXITCODE -ne 0) { throw "TypeScript tests failed" }
    Pop-Location

    Write-Host "`n[2/8] Running MCP server tests..." -ForegroundColor Green
    $servers = @('fs-mcp', 'content-mcp', 'template-mcp', 'graph-mcp', 'registry-mcp')
    foreach ($server in $servers) {
        Write-Host "  Testing $server..."
        Push-Location (Join-Path $projectRoot "docker/mcp-servers/$server")
        python -m pytest tests/ -v --tb=short
        if ($LASTEXITCODE -ne 0) { throw "$server tests failed" }
        Pop-Location
    }

    Write-Host "`n[3/8] Running agent tests..." -ForegroundColor Green
    $agents = @('venture-generator', 'site-creator', 'content-writer', 'graph-builder', 'qa-validator')
    foreach ($agent in $agents) {
        Write-Host "  Testing $agent..."
        Push-Location (Join-Path $projectRoot "docker/agents/$agent")
        python -m pytest tests/ -v --tb=short
        if ($LASTEXITCODE -ne 0) { throw "$agent tests failed" }
        Pop-Location
    }
}

# Step 2: Run agents (Python with importlib for dash-named dirs)
Write-Host "`n[4/8] Running venture-generator..." -ForegroundColor Green
Push-Location $projectRoot
$vgScript = @'
import sys, json, importlib.util
from pathlib import Path

root = Path('.')
spec = importlib.util.spec_from_file_location('vg', str(root / 'docker/agents/venture-generator/agent.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with open('ventures.json') as f:
    data = json.load(f)

agent = mod.VentureGenerator(data_root='.')
result = agent.run(data)
print('  Groups: %d, Ventures: %d, Offerings: %d' % (result['groups_processed'], result['ventures_created'], result['offerings_created']))
if result['success']:
    with open('ventures.json', 'w') as f:
        json.dump(result['ventures_data'], f, indent=2)
    print('  ventures.json updated')
else:
    print('  Errors: %s' % result['errors'])
    sys.exit(1)
'@
python -c $vgScript
if ($LASTEXITCODE -ne 0) { throw "venture-generator failed" }
Pop-Location

Write-Host "`n[5/8] Running site-creator..." -ForegroundColor Green
Push-Location $projectRoot
$scScript = @'
import sys, json, importlib.util
from pathlib import Path

root = Path('.')
spec = importlib.util.spec_from_file_location('sc', str(root / 'docker/agents/site-creator/agent.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with open('ventures.json') as f:
    data = json.load(f)

agent = mod.SiteCreator(data_root='.')
result = agent.run(data)
print('  Dirs: %d, Pages: %d, Metadata: %d' % (result['directories_created'], result['pages_created'], result['metadata_created']))
print('  Success: %s' % result['success'])
if not result['success']:
    print('  Errors: %s' % result['errors'])
    sys.exit(1)
'@
python -c $scScript
if ($LASTEXITCODE -ne 0) { throw "site-creator failed" }
Pop-Location

Write-Host "`n[6/8] Running content-writer..." -ForegroundColor Green
Push-Location $projectRoot
$cwScript = @'
import sys, json, importlib.util
from pathlib import Path

root = Path('.')
spec = importlib.util.spec_from_file_location('cw', str(root / 'docker/agents/content-writer/agent.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with open('ventures.json') as f:
    data = json.load(f)

agent = mod.ContentWriter(data_root='.')
result = agent.run(data)
print('  Enriched: %d, SEO: %d' % (result['pages_enriched'], result['seo_generated']))
print('  Success: %s' % result['success'])
if not result['success']:
    print('  Errors: %s' % result['errors'])
    sys.exit(1)
'@
python -c $cwScript
if ($LASTEXITCODE -ne 0) { throw "content-writer failed" }
Pop-Location

Write-Host "`n[7/8] Running graph-builder..." -ForegroundColor Green
Push-Location $projectRoot
$gbScript = @'
import sys, json, importlib.util
from pathlib import Path

root = Path('.')
spec = importlib.util.spec_from_file_location('gb', str(root / 'docker/agents/graph-builder/agent.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with open('ventures.json') as f:
    data = json.load(f)

agent = mod.GraphBuilder(data_root='.')
result = agent.run(data)
print('  Nav: %s, Cross-links: %d' % (result['nav_updated'], result['cross_links_added']))
print('  Success: %s' % result['success'])
if not result['success']:
    print('  Errors: %s' % result['errors'])
    sys.exit(1)
'@
python -c $gbScript
if ($LASTEXITCODE -ne 0) { throw "graph-builder failed" }
Pop-Location

Write-Host "`n[7.5/8] Running qa-validator..." -ForegroundColor Green
Push-Location $projectRoot
$qaScript = @'
import sys, json, importlib.util
from pathlib import Path

root = Path('.')
spec = importlib.util.spec_from_file_location('qa', str(root / 'docker/agents/qa-validator/agent.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with open('ventures.json') as f:
    data = json.load(f)

agent = mod.QaValidator(data_root='.')
result = agent.run(data)
print('  Validated: %d, Orphans: %d, Passed: %s' % (result['pages_validated'], len(result['orphan_pages']), result['validation_passed']))
print('  Success: %s' % result['success'])
if not result['success']:
    print('  Errors: %s' % result['errors'])
    sys.exit(1)
'@
python -c $qaScript
if ($LASTEXITCODE -ne 0) { throw "qa-validator failed" }
Pop-Location

# Step 3: Validate and health check
Write-Host "`n[8/8] Running health check and validation..." -ForegroundColor Green
Push-Location $projectRoot
python src/scripts/health-check.py sites/leo-global-holdings
python src/scripts/drift-detection.py .
Pop-Location

# Summary
Write-Host "`n=== Pipeline Complete ===" -ForegroundColor Cyan
Write-Host "Generated files:" -ForegroundColor Green
Write-Host "  - ventures.json (updated)"
Write-Host "  - sites/leo-global-holdings/ (all pages)"
Write-Host ""
Write-Host "To deploy: copy sites/leo-global-holdings/ to docs/" -ForegroundColor Yellow
