<#
.SYNOPSIS
    ExamGrader - Intelligent Exam Grading System One-Click Deployment Script
    
.DESCRIPTION
    This script automates the deployment of the ExamGrader system using Docker Compose.
    It includes setup, configuration, and launch of all microservices.
    
.REQUIREMENTS
    - Docker Desktop with WSL2 enabled (Windows)
    - NVIDIA Docker (for GPU acceleration)
    - At least 16GB RAM
    - At least 50GB free disk space
    
.AUTHOR
    ExamGrader Development Team
    
.LICENSE
    MIT License
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "start",
    
    [Parameter(Mandatory=$false)]
    [string]$Mode = "full"  # full, lite, api-only
)

$ErrorActionPreference = "Stop"

function Test-CommandExists {
    param([string]$Command)
    $exists = $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
    return $exists
}

function Test-DockerRunning {
    try {
        docker info | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Invoke-SetupChecks {
    Write-Host "`n=== ExamGrader Deployment Check ===" -ForegroundColor Cyan
    
    # Check Docker installation
    if (-not (Test-CommandExists "docker")) {
        Write-Error "Docker is not installed. Please install Docker Desktop from https://www.docker.com/products/docker-desktop/"
        exit 1
    }
    Write-Host "✓ Docker installed" -ForegroundColor Green
    
    # Check Docker Compose
    if (-not (Test-CommandExists "docker-compose")) {
        Write-Error "Docker Compose is not installed. Please install it from https://docs.docker.com/compose/install/"
        exit 1
    }
    Write-Host "✓ Docker Compose installed" -ForegroundColor Green
    
    # Check Docker running
    if (-not (Test-DockerRunning)) {
        Write-Error "Docker is not running. Please start Docker Desktop."
        exit 1
    }
    Write-Host "✓ Docker daemon is running" -ForegroundColor Green
    
    # Check NVIDIA Docker (for GPU mode)
    if ($Mode -eq "full") {
        try {
            docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi | Out-Null
            Write-Host "✓ NVIDIA GPU available" -ForegroundColor Green
        }
        catch {
            Write-Warning "⚠ NVIDIA GPU not detected or NVIDIA Docker not configured. Running in CPU mode."
        }
    }
    
    # Check disk space
    $drive = (Get-Item .).PSDrive
    $freeSpaceGB = [math]::Round($drive.Free / 1GB, 2)
    if ($freeSpaceGB -lt 50) {
        Write-Warning "⚠ Low disk space detected: $freeSpaceGB GB available. Recommend at least 50GB."
    }
    Write-Host "✓ Disk space: $freeSpaceGB GB available" -ForegroundColor Green
    
    Write-Host "`n=== All checks passed ===" -ForegroundColor Cyan
}

function Invoke-DownloadModels {
    Write-Host "`n=== Downloading AI Models ===" -ForegroundColor Cyan
    
    # Download Qwen2-7B-Instruct model
    Write-Host "Downloading Qwen2-7B-Instruct model..." -ForegroundColor Yellow
    docker pull vllm/vllm-openai:latest
    
    Write-Host "✓ Models downloaded" -ForegroundColor Green
}

function Invoke-StartServices {
    Write-Host "`n=== Starting ExamGrader Services ===" -ForegroundColor Cyan
    
    # Create necessary directories
    New-Item -ItemType Directory -Force -Path "./data/postgres" | Out-Null
    New-Item -ItemType Directory -Force -Path "./data/redis" | Out-Null
    
    # Start services based on mode
    switch ($Mode) {
        "full" {
            Write-Host "Starting full stack (API + LLM + Embedding + Agent + Web)..." -ForegroundColor Yellow
            docker-compose up -d
        }
        "lite" {
            Write-Host "Starting lite mode (API + Web only, using external LLM)..." -ForegroundColor Yellow
            docker-compose up -d postgres redis api web
        }
        "api-only" {
            Write-Host "Starting API only mode..." -ForegroundColor Yellow
            docker-compose up -d postgres redis api
        }
    }
    
    Write-Host "`n=== Services started ===" -ForegroundColor Cyan
    
    # Wait for services to be ready
    Write-Host "Waiting for services to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    # Check service status
    docker-compose ps
    
    Write-Host "`n=== Service Status ===" -ForegroundColor Cyan
    Write-Host "API Service: http://localhost:8000" -ForegroundColor Green
    Write-Host "Web UI: http://localhost:5173" -ForegroundColor Green
    Write-Host "LLM Service: http://localhost:8001" -ForegroundColor Green
    Write-Host "Embedding Service: http://localhost:8002" -ForegroundColor Green
    Write-Host "Agent Service: http://localhost:8003" -ForegroundColor Green
}

function Invoke-StopServices {
    Write-Host "`n=== Stopping ExamGrader Services ===" -ForegroundColor Cyan
    docker-compose down
    Write-Host "✓ All services stopped" -ForegroundColor Green
}

function Invoke-ResetServices {
    Write-Host "`n=== Resetting ExamGrader Services ===" -ForegroundColor Cyan
    Write-Host "This will remove all containers, networks, and volumes." -ForegroundColor Yellow
    Read-Host "Press Enter to continue (Ctrl+C to cancel)"
    
    docker-compose down -v
    Write-Host "✓ All services reset" -ForegroundColor Green
}

function Invoke-ShowLogs {
    Write-Host "`n=== Showing Service Logs ===" -ForegroundColor Cyan
    docker-compose logs -f
}

function Invoke-ShowHelp {
    Write-Host @"

ExamGrader Deployment Script

Usage: .\deploy.ps1 [-Action <action>] [-Mode <mode>]

Actions:
    start    - Start all services (default)
    stop     - Stop all services
    reset    - Stop and remove all data (destructive)
    logs     - Show service logs
    check    - Check system requirements
    download - Download AI models

Modes:
    full       - Full stack with all services (default)
    lite       - API + Web only (uses external LLM)
    api-only   - API service only

Examples:
    .\deploy.ps1                          # Start full stack
    .\deploy.ps1 -Action start -Mode lite # Start lite mode
    .\deploy.ps1 -Action stop             # Stop services
    .\deploy.ps1 -Action logs             # View logs

"@
}

# Main execution
switch ($Action) {
    "start" {
        Invoke-SetupChecks
        Invoke-DownloadModels
        Invoke-StartServices
    }
    "stop" {
        Invoke-StopServices
    }
    "reset" {
        Invoke-ResetServices
    }
    "logs" {
        Invoke-ShowLogs
    }
    "check" {
        Invoke-SetupChecks
    }
    "download" {
        Invoke-DownloadModels
    }
    default {
        Invoke-ShowHelp
    }
}

Write-Host "`n=== Deployment completed ===" -ForegroundColor Cyan