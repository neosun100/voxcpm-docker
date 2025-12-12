#!/bin/bash

set -e

echo "🚀 VoxCPM Docker Startup Script"
echo "================================"

# Check nvidia-docker
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ nvidia-smi not found. Please install NVIDIA drivers."
    exit 1
fi

echo "✅ NVIDIA GPU detected:"
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader

# Auto-select least used GPU
echo ""
echo "🔍 Selecting GPU with lowest memory usage..."
GPU_ID=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | \
         sort -t',' -k2 -n | head -1 | cut -d',' -f1)
export NVIDIA_VISIBLE_DEVICES=$GPU_ID
echo "✅ Selected GPU: $GPU_ID"

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
fi

# Update GPU ID in .env
sed -i "s/^NVIDIA_VISIBLE_DEVICES=.*/NVIDIA_VISIBLE_DEVICES=$GPU_ID/" .env

# Check port availability
PORT=$(grep "^PORT=" .env | cut -d'=' -f2)
if netstat -tuln | grep -q ":$PORT "; then
    echo "⚠️  Port $PORT is already in use. Please change PORT in .env"
    exit 1
fi

echo ""
echo "🐳 Starting Docker Compose..."
docker-compose up -d --build

echo ""
echo "✅ VoxCPM is starting..."
echo "📍 Access points:"
echo "   - UI:      http://0.0.0.0:$PORT"
echo "   - API:     http://0.0.0.0:$PORT/api"
echo "   - Swagger: http://0.0.0.0:$PORT/docs"
echo "   - MCP:     Use mcp_client.json config"
echo ""
echo "📊 View logs: docker-compose logs -f"
echo "🛑 Stop:      docker-compose down"
