#!/bin/bash

# DocumentAgent Docker Deployment Script
set -e

echo "🚀 Deploying DocumentAgent with Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads document_vector_db ssl

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running successfully!"
else
    echo "❌ Some services failed to start. Check logs with: docker-compose logs"
    exit 1
fi

# Pull required Ollama models
echo "🤖 Pulling required Ollama models..."
docker-compose exec ollama ollama pull gemma3:4b
docker-compose exec ollama ollama pull nomic-embed-text

echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Access your application:"
echo "   - Web App: http://localhost:5000"
echo "   - Ollama API: http://localhost:11434"
echo ""
echo "🔧 Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Restart services: docker-compose restart"
echo "   - Update services: docker-compose pull && docker-compose up -d"
echo ""
echo "📁 Data persistence:"
echo "   - Uploads: ./uploads/"
echo "   - Vector DB: ./document_vector_db/"
echo "   - Ollama models: ./ollama_data/ (Docker volume)"
