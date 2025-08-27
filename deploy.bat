@echo off
echo 🚀 Deploying DocumentAgent with Docker...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "document_vector_db" mkdir document_vector_db
if not exist "ssl" mkdir ssl

REM Build and start services
echo 🔨 Building and starting services...
docker-compose up -d --build

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Check service health
echo 🏥 Checking service health...
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo ❌ Some services failed to start. Check logs with: docker-compose logs
    pause
    exit /b 1
) else (
    echo ✅ Services are running successfully!
)

REM Pull required Ollama models
echo 🤖 Pulling required Ollama models...
docker-compose exec ollama ollama pull gemma3:4b
docker-compose exec ollama ollama pull nomic-embed-text

echo 🎉 Deployment completed successfully!
echo.
echo 📋 Access your application:
echo    - Web App: http://localhost:5000
echo    - Ollama API: http://localhost:11434
echo.
echo 🔧 Useful commands:
echo    - View logs: docker-compose logs -f
echo    - Stop services: docker-compose down
echo    - Restart services: docker-compose restart
echo    - Update services: docker-compose pull ^&^& docker-compose up -d
echo.
echo 📁 Data persistence:
echo    - Uploads: .\uploads\
echo    - Vector DB: .\document_vector_db\
echo    - Ollama models: .\ollama_data\ (Docker volume)
echo.
pause
