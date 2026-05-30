#!/bin/bash

#
# SYNOPSIS
#     ExamGrader - Intelligent Exam Grading System One-Click Deployment Script
#
# DESCRIPTION
#     This script automates the deployment of the ExamGrader system using Docker Compose.
#     It includes setup, configuration, and launch of all microservices.
#
# REQUIREMENTS
#     - Docker and Docker Compose installed
#     - NVIDIA Docker (for GPU acceleration)
#     - At least 16GB RAM
#     - At least 50GB free disk space
#
# AUTHOR
#     ExamGrader Development Team
#
# LICENSE
#     Apache License 2.0
#

set -e

ACTION="${1:-start}"
MODE="${2:-full}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

test_command_exists() {
    command -v "$1" >/dev/null 2>&1
}

test_docker_running() {
    docker info >/dev/null 2>&1
}

invoke_setup_checks() {
    echo -e "\n${CYAN}=== ExamGrader Deployment Check ===${NC}"
    
    # Check Docker installation
    if ! test_command_exists docker; then
        echo -e "${RED}Docker is not installed. Please install Docker from https://www.docker.com/products/docker-desktop/${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker installed${NC}"
    
    # Check Docker Compose
    if ! test_command_exists docker-compose; then
        echo -e "${RED}Docker Compose is not installed. Please install it from https://docs.docker.com/compose/install/${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
    
    # Check Docker running
    if ! test_docker_running; then
        echo -e "${RED}Docker is not running. Please start Docker.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker daemon is running${NC}"
    
    # Check NVIDIA Docker (for GPU mode)
    if [ "$MODE" = "full" ]; then
        if docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi >/dev/null 2>&1; then
            echo -e "${GREEN}✓ NVIDIA GPU available${NC}"
        else
            echo -e "${YELLOW}⚠ NVIDIA GPU not detected or NVIDIA Docker not configured. Running in CPU mode.${NC}"
        fi
    fi
    
    # Check disk space
    free_space_gb=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$free_space_gb" -lt 50 ]; then
        echo -e "${YELLOW}⚠ Low disk space detected: ${free_space_gb}GB available. Recommend at least 50GB.${NC}"
    fi
    echo -e "${GREEN}✓ Disk space: ${free_space_gb} GB available${NC}"
    
    echo -e "\n${CYAN}=== All checks passed ===${NC}"
}

invoke_download_models() {
    echo -e "\n${CYAN}=== Downloading AI Models ===${NC}"
    
    # Download vLLM image
    echo -e "${YELLOW}Downloading vLLM image...${NC}"
    docker pull vllm/vllm-openai:latest
    
    echo -e "${GREEN}✓ Models downloaded${NC}"
}

invoke_start_services() {
    echo -e "\n${CYAN}=== Starting ExamGrader Services ===${NC}"
    
    # Create necessary directories
    mkdir -p ./data/postgres
    mkdir -p ./data/redis
    
    # Start services based on mode
    case "$MODE" in
        full)
            echo -e "${YELLOW}Starting full stack (API + LLM + Embedding + Agent + Web)...${NC}"
            docker-compose up -d
            ;;
        lite)
            echo -e "${YELLOW}Starting lite mode (API + Web only, using external LLM)...${NC}"
            docker-compose up -d postgres redis api web
            ;;
        api-only)
            echo -e "${YELLOW}Starting API only mode...${NC}"
            docker-compose up -d postgres redis api
            ;;
    esac
    
    echo -e "\n${CYAN}=== Services started ===${NC}"
    
    # Wait for services to be ready
    echo -e "${YELLOW}Waiting for services to initialize...${NC}"
    sleep 30
    
    # Check service status
    docker-compose ps
    
    echo -e "\n${CYAN}=== Service Status ===${NC}"
    echo -e "${GREEN}API Service: http://localhost:8000${NC}"
    echo -e "${GREEN}Web UI: http://localhost:5173${NC}"
    echo -e "${GREEN}LLM Service: http://localhost:8001${NC}"
    echo -e "${GREEN}Embedding Service: http://localhost:8002${NC}"
    echo -e "${GREEN}Agent Service: http://localhost:8003${NC}"
}

invoke_stop_services() {
    echo -e "\n${CYAN}=== Stopping ExamGrader Services ===${NC}"
    docker-compose down
    echo -e "${GREEN}✓ All services stopped${NC}"
}

invoke_reset_services() {
    echo -e "\n${CYAN}=== Resetting ExamGrader Services ===${NC}"
    echo -e "${YELLOW}This will remove all containers, networks, and volumes.${NC}"
    read -p "Press Enter to continue (Ctrl+C to cancel): "
    
    docker-compose down -v
    echo -e "${GREEN}✓ All services reset${NC}"
}

invoke_show_logs() {
    echo -e "\n${CYAN}=== Showing Service Logs ===${NC}"
    docker-compose logs -f
}

invoke_show_help() {
    echo -e "
${CYAN}ExamGrader Deployment Script${NC}

Usage: ./deploy.sh [action] [mode]

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
    ./deploy.sh                          # Start full stack
    ./deploy.sh start lite               # Start lite mode
    ./deploy.sh stop                     # Stop services
    ./deploy.sh logs                     # View logs

"
}

# Main execution
case "$ACTION" in
    start)
        invoke_setup_checks
        invoke_download_models
        invoke_start_services
        ;;
    stop)
        invoke_stop_services
        ;;
    reset)
        invoke_reset_services
        ;;
    logs)
        invoke_show_logs
        ;;
    check)
        invoke_setup_checks
        ;;
    download)
        invoke_download_models
        ;;
    help|--help|-h)
        invoke_show_help
        ;;
    *)
        echo -e "${RED}Unknown action: $ACTION${NC}"
        invoke_show_help
        exit 1
        ;;
esac

echo -e "\n${CYAN}=== Deployment completed ===${NC}"
