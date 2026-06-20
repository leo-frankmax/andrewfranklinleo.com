#!/usr/bin/env pwsh
# Runner Setup Script for Andrew Franklin Leo CMS
# Run this on the self-hosted runner machine to configure the environment.

param(
    [string]$GitHubUrl = "https://github.com/andrewfranklinleo/andrewfranklinleo.com",
    [string]$Token = "",
    [switch]$InstallDocker,
    [switch]$InstallNode,
    [switch]$InstallPython
)

$ErrorActionPreference = "Stop"

Write-Host "=== Andrew Franklin Leo CMS - Runner Setup ===" -ForegroundColor Cyan

# Check prerequisites
function Test-Command($cmd) {
    return [bool](Get-Command $cmd -ErrorAction SilentlyContinue)
}

# 1. Check/install Docker Desktop
if ($InstallDocker -or -not (Test-Command "docker")) {
    Write-Host "Installing Docker Desktop..." -ForegroundColor Yellow
    winget install Docker.DockerDesktop --accept-source-agreements --accept-package-agreements
    Write-Host "Docker Desktop installed. Please restart your terminal." -ForegroundColor Green
}

# 2. Check/install Node.js
if ($InstallNode -or -not (Test-Command "node")) {
    Write-Host "Installing Node.js..." -ForegroundColor Yellow
    winget install OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
    Write-Host "Node.js installed." -ForegroundColor Green
}

# 3. Check/install Python
if ($InstallPython -or -not (Test-Command "python")) {
    Write-Host "Installing Python..." -ForegroundColor Yellow
    winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    Write-Host "Python installed." -ForegroundColor Green
}

# 4. Verify versions
Write-Host "`nChecking versions..." -ForegroundColor Cyan
if (Test-Command "docker") {
    $dockerVersion = docker --version
    Write-Host "  Docker: $dockerVersion" -ForegroundColor Green
} else {
    Write-Host "  Docker: NOT FOUND" -ForegroundColor Red
}

if (Test-Command "node") {
    $nodeVersion = node --version
    Write-Host "  Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "  Node.js: NOT FOUND" -ForegroundColor Red
}

if (Test-Command "python") {
    $pythonVersion = python --version
    Write-Host "  Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  Python: NOT FOUND" -ForegroundColor Red
}

# 5. Install runner if token provided
if ($Token) {
    $runnerDir = "C:\Users\Andrew Franklin Leo\actions-runner"
    if (-not (Test-Path $runnerDir)) {
        Write-Host "`nDownloading GitHub Actions runner..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Force -Path $runnerDir | Out-Null
        $runnerUrl = "https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-win-x64-2.321.0.zip"
        Invoke-WebRequest -Uri $runnerUrl -OutFile "$runnerDir\runner.zip"
        Expand-Archive -Path "$runnerDir\runner.zip" -DestinationPath $runnerDir -Force
        Remove-Item "$runnerDir\runner.zip"
    }

    Write-Host "Configuring runner..." -ForegroundColor Yellow
    cd $runnerDir
    .\config.cmd --url $GitHubUrl --token $Token --unattended
    .\svc.cmd install
    .\svc.cmd start
    Write-Host "Runner installed and started as Windows service." -ForegroundColor Green
}

# 6. Install npm dependencies
Write-Host "`nInstalling project dependencies..." -ForegroundColor Yellow
$projectRoot = "C:\Users\Andrew Franklin Leo\Documents\Projects\andrewfranklinleo.com"
if (Test-Path "$projectRoot\package.json") {
    cd $projectRoot
    npm ci
    Write-Host "npm dependencies installed." -ForegroundColor Green
}

# 7. Install Python test dependencies
Write-Host "`nInstalling Python test dependencies..." -ForegroundColor Yellow
pip install pytest --quiet
Write-Host "pytest installed." -ForegroundColor Green

Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "Runner is ready for the Andrew Franklin Leo CMS pipeline." -ForegroundColor Green
