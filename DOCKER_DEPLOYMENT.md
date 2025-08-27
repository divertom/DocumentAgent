# 🐳 DocumentAgent Docker Deployment Guide

This guide covers deploying DocumentAgent with Docker on any machine, including Ollama LLM integration.

## 🚀 **Quick Start (Recommended)**

### **1. Prerequisites**
- Docker Desktop installed
- Docker Compose installed
- At least 8GB RAM (16GB recommended for LLM models)
- 20GB+ free disk space

### **2. One-Command Deployment**

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```cmd
deploy.bat
```

### **3. Manual Deployment**
```bash
# Create directories
mkdir -p uploads document_vector_db ssl

# Start services
docker-compose up -d --build

# Pull required models
docker-compose exec ollama ollama pull gemma3:4b
docker-compose exec ollama ollama pull nomic-embed-text
```

## 📋 **Deployment Options**

### **Option A: Production (Recommended)**
```bash
docker-compose up -d --build
```
- Includes Nginx reverse proxy
- Optimized for production use
- SSL support (configure in nginx.conf)

### **Option B: Development**
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```
- Hot reload enabled
- Volume mounting for live code changes
- Debug mode enabled

### **Option C: Ollama Only**
```bash
docker run -d -p 11434:11434 -v ollama_data:/root/.ollama ollama/ollama:latest
```
- Just the LLM service
- Useful if you want to run the web app separately

## 🔧 **Configuration**

### **Environment Variables**
```bash
# In docker-compose.yml
environment:
  - FLASK_ENV=production          # production/development
  - VECTOR_DB_PATH=/app/document_vector_db
  - UPLOAD_FOLDER=/app/uploads
  - OLLAMA_HOST=http://ollama:11434
```

### **Port Configuration**
```yaml
ports:
  - "5000:5000"      # Web application
  - "11434:11434"    # Ollama API
  - "80:80"          # Nginx (production)
  - "443:443"        # Nginx HTTPS (production)
```

## 📁 **Data Persistence**

### **Volumes**
- **`./uploads/`** → PDF uploads
- **`./document_vector_db/`** → Vector database
- **`ollama_data`** → Ollama models (Docker volume)

### **Backup Strategy**
```bash
# Backup data
tar -czf backup_$(date +%Y%m%d).tar.gz uploads/ document_vector_db/

# Backup Ollama models
docker run --rm -v ollama_data:/data -v $(pwd):/backup alpine tar -czf /backup/ollama_models_$(date +%Y%m%d).tar.gz /data
```

## 🌐 **Access Points**

### **Local Access**
- **Web App**: http://localhost:5000
- **Ollama API**: http://localhost:11434
- **Health Check**: http://localhost:5000/health

### **Network Access**
- **Web App**: http://YOUR_IP:5000
- **Ollama API**: http://YOUR_IP:11434

## 🔍 **Monitoring & Logs**

### **View Logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f documentagent
docker-compose logs -f ollama

# Last 100 lines
docker-compose logs --tail=100
```

### **Service Status**
```bash
docker-compose ps
docker-compose top
```

### **Health Checks**
```bash
# Web app health
curl http://localhost:5000/health

# Ollama health
docker-compose exec ollama ollama list
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Port Already in Use**
```bash
# Check what's using the port
netstat -tulpn | grep :5000

# Stop conflicting service or change port in docker-compose.yml
```

#### **2. Ollama Models Not Loading**
```bash
# Check Ollama logs
docker-compose logs ollama

# Pull models manually
docker-compose exec ollama ollama pull gemma3:4b
docker-compose exec ollama ollama pull nomic-embed-text
```

#### **3. Memory Issues**
```bash
# Check container memory usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
```

#### **4. Permission Issues**
```bash
# Fix directory permissions
sudo chown -R $USER:$USER uploads/ document_vector_db/
chmod 755 uploads/ document_vector_db/
```

### **Reset Everything**
```bash
# Stop and remove everything
docker-compose down -v
docker system prune -a

# Rebuild from scratch
docker-compose up -d --build
```

## 🔄 **Updates & Maintenance**

### **Update Application**
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### **Update Ollama Models**
```bash
# Update specific model
docker-compose exec ollama ollama pull gemma3:4b

# Update all models
docker-compose exec ollama ollama pull --all
```

### **System Updates**
```bash
# Update Docker images
docker-compose pull
docker-compose up -d

# Clean up old images
docker system prune -a
```

## 🛡️ **Security Considerations**

### **Production Security**
1. **Change default ports** in docker-compose.yml
2. **Enable HTTPS** with SSL certificates
3. **Set up firewall** rules
4. **Use environment variables** for secrets
5. **Regular security updates**

### **Network Security**
```bash
# Restrict network access
# In docker-compose.yml, change:
ports:
  - "127.0.0.1:5000:5000"  # Only localhost access
```

## 📊 **Performance Tuning**

### **Resource Limits**
```yaml
# In docker-compose.yml
services:
  documentagent:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
  ollama:
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
```

### **Optimization Tips**
1. **Use SSD storage** for better I/O performance
2. **Allocate sufficient RAM** for Ollama models
3. **Enable Docker BuildKit** for faster builds
4. **Use multi-stage builds** for smaller images

## 🔗 **Integration Examples**

### **External Ollama Instance**
```yaml
# If Ollama is running on another machine
environment:
  - OLLAMA_HOST=http://192.168.1.100:11434
```

### **Load Balancer**
```yaml
# Multiple DocumentAgent instances
services:
  documentagent1:
    ports:
      - "5001:5000"
  documentagent2:
    ports:
      - "5002:5000"
```

## 📚 **Additional Resources**

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Flask Production Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)

## 🆘 **Getting Help**

If you encounter issues:

1. **Check logs**: `docker-compose logs -f`
2. **Verify Docker**: `docker --version && docker-compose --version`
3. **Check resources**: `docker stats`
4. **Restart services**: `docker-compose restart`
5. **Rebuild**: `docker-compose down && docker-compose up -d --build`

---

**Happy Deploying! 🎉**
