#!/bin/bash
# AgriPOS Quick Start Script

set -e

echo "========================================"
echo "  AgriPOS System - Starting..."
echo "========================================"

# Copy .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env from .env.example"
    echo "  Please update .env with your settings!"
fi

# Start all services
echo "Starting services with Docker Compose..."
docker compose up -d

echo ""
echo "========================================"
echo "  AgriPOS is running!"
echo "========================================"
echo "  Frontend:  http://localhost"
echo "  API Docs:  http://localhost:8000/api/docs"
echo "  pgAdmin:   http://localhost:5050 (dev profile)"
echo ""
echo "  Default login:"
echo "    Username: admin"
echo "    Password: admin1234"
echo "========================================"
