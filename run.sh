#!/bin/bash
# Multi-environment startup script for Habit Tracker API

set -e

# Default environment
ENV=${APP_ENV:-local}

echo "🚀 Starting Habit Tracker API in $ENV environment..."

case $ENV in
  local)
    echo "📍 Local Development"
    echo "   Database: localhost:5432"
    echo "   S3: localhost:4566"
    echo "   Jaeger: localhost (disabled)"
    export APP_ENV=local
    export DEBUG=true
    python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    ;;

  docker)
    echo "📍 Docker Compose Test Environment"
    echo "   Database: db:5432"
    echo "   S3: localstack:4566"
    echo "   Jaeger: jaeger:6831"
    export APP_ENV=docker
    export DEBUG=false
    python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
    ;;

  minikube)
    echo "📍 Minikube Kubernetes"
    echo "   Database: habit-tracker-postgres:5432"
    echo "   S3: habit-tracker-s3:9000"
    echo "   Jaeger: habit-tracker-jaeger:6831"
    export APP_ENV=minikube
    export DEBUG=false
    python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
    ;;

  *)
    echo "❌ Unknown environment: $ENV"
    echo "Valid options: local, docker, minikube"
    exit 1
    ;;
esac
