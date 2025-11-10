# Deployment Guide

## Deployment Options

Otis offers three deployment configurations:

### Option 1: Minimal Core (8GB RAM) - Recommended for Development
```bash
docker-compose -f docker-compose.core.yml up -d
```
**Services**: API, Ollama, Chroma, PostgreSQL, Redis, Jaeger (6 services)

### Option 2: Full Platform (32GB RAM) - Production with Red/Blue Team
```bash
docker-compose -f docker-compose.fixed.yml up -d
```
**Adds**: Red Team tools, Blue Team pipeline, C2 server, Elasticsearch, Vector, ElastAlert

### Option 3: Local Development
```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
python src/main.py
```

## Prerequisites

- Docker & Docker Compose
- 8GB RAM minimum (core), 32GB recommended (full platform)
- PostgreSQL database (included in Docker Compose)
- Ollama server (included in Docker Compose)
- (Optional) Telegram Bot for approval workflow

## Production Deployment

### 1. Environment Setup

Create a production `.env` file:

```bash
# Application
APP_NAME=Otis Cybersecurity AI Agent
APP_VERSION=0.1.0
DEBUG=false
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1

# Security - CHANGE THESE!
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database - PostgreSQL for production
DATABASE_URL=postgresql://otis:secure_password@postgres:5432/otis

# Ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=deepseek-r1:7b
OLLAMA_TIMEOUT=300

# Chroma
CHROMA_PERSIST_DIRECTORY=/app/chroma_data
CHROMA_COLLECTION_NAME=cybersecurity_knowledge

# Telegram
TELEGRAM_BOT_TOKEN=your-production-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-admin-chat-id
TELEGRAM_APPROVAL_TIMEOUT=300

# Docker Sandbox
DOCKER_SANDBOX_IMAGE=python:3.11-slim
DOCKER_SANDBOX_TIMEOUT=60
DOCKER_SANDBOX_MEMORY_LIMIT=512m
DOCKER_SANDBOX_CPU_LIMIT=1.0

# Feature Flags
ENABLE_APPROVAL_GATE=true
ENABLE_CODE_EXECUTION=true
ENABLE_THREAT_INTEL=true
```

### 2. Deploy with Docker Compose

**Core Deployment (8GB RAM):**
```bash
# Build images
docker-compose -f docker-compose.core.yml build

# Start services
docker-compose -f docker-compose.core.yml up -d

# Check status
docker-compose -f docker-compose.core.yml ps

# View logs
docker-compose -f docker-compose.core.yml logs -f
```

**Full Platform (32GB RAM):**
```bash
# Build images
docker-compose -f docker-compose.fixed.yml build

# Start services
docker-compose -f docker-compose.fixed.yml up -d

# Check status
docker-compose -f docker-compose.fixed.yml ps

# View logs
docker-compose -f docker-compose.fixed.yml logs -f
```

### 3. Initialize Database

```bash
# Run migrations
docker-compose exec otis alembic upgrade head

# Create admin user
docker-compose exec otis python scripts/create_admin.py

# Initialize RAG data
docker-compose exec otis python scripts/init_rag_data.py
```

### 4. Setup Ollama Model

```bash
# Pull DeepSeek-R1 model
docker-compose exec ollama ollama pull deepseek-r1:7b

# Verify model
docker-compose exec ollama ollama list
```

### 5. Configure Telegram Bot

1. Create a bot with [@BotFather](https://t.me/BotFather)
2. Get your bot token
3. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
4. Update `.env` with these values
5. Restart the service: `docker-compose restart otis`

### 6. Setup Reverse Proxy (Recommended)

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name otis.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### SSL with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d otis.yourdomain.com

# Auto-renewal is configured by certbot
```

### 7. Monitoring

#### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

#### Logs

```bash
# Application logs
docker-compose logs -f otis

# Database logs
docker-compose logs -f postgres

# Ollama logs
docker-compose logs -f ollama
```

### 8. Backup Strategy

#### Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U otis otis > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U otis otis < backup.sql
```

#### Chroma Data Backup

```bash
# Backup vector store
tar -czf chroma_backup_$(date +%Y%m%d).tar.gz chroma_data/

# Restore
tar -xzf chroma_backup.tar.gz
```

## Kubernetes Deployment

### 1. Create ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: otis-config
data:
  DATABASE_URL: "postgresql://otis:password@postgres-service:5432/otis"
  OLLAMA_BASE_URL: "http://ollama-service:11434"
  # Add other config...
```

### 2. Create Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: otis-secrets
type: Opaque
stringData:
  SECRET_KEY: "your-secret-key"
  TELEGRAM_BOT_TOKEN: "your-bot-token"
```

### 3. Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otis-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: otis
  template:
    metadata:
      labels:
        app: otis
    spec:
      containers:
      - name: otis
        image: otis:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: otis-config
        - secretRef:
            name: otis-secrets
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

### 4. Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: otis-service
spec:
  selector:
    app: otis
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Performance Tuning

### Application

- Use Gunicorn with multiple workers
- Enable connection pooling for database
- Configure Redis for caching (optional)

### Database

- Tune PostgreSQL settings
- Create appropriate indexes
- Regular VACUUM operations

### Ollama

- Allocate sufficient GPU memory
- Monitor model loading time
- Consider model caching strategies

## Security Hardening

1. **Change default credentials**
2. **Enable HTTPS only**
3. **Configure firewall rules**
4. **Regular security updates**
5. **Enable audit logging**
6. **Implement rate limiting**
7. **Setup intrusion detection**
8. **Regular backups**

## Troubleshooting

### Common Issues

#### Ollama Connection Error
```bash
# Check Ollama status
docker-compose logs ollama

# Restart Ollama
docker-compose restart ollama
```

#### Database Connection Error
```bash
# Check PostgreSQL status
docker-compose logs postgres

# Verify connection
docker-compose exec postgres psql -U otis -d otis
```

#### Chroma Permission Issues
```bash
# Fix permissions
sudo chown -R 1000:1000 chroma_data/
```

## Scaling

### Horizontal Scaling

- Deploy multiple instances behind load balancer
- Use shared PostgreSQL and Chroma instances
- Configure session affinity if needed

### Vertical Scaling

- Increase container resources
- Allocate more GPU memory for Ollama
- Optimize database configuration

## Maintenance

### Regular Tasks

- Update dependencies: `pip install -r requirements.txt --upgrade`
- Update Docker images: `docker-compose pull`
- Backup databases: Daily/Weekly
- Review logs: Daily
- Security updates: Weekly
- Performance monitoring: Continuous

### Rollback Procedure

```bash
# Tag current version
docker tag otis:latest otis:rollback

# Revert to previous version
docker-compose down
git checkout <previous-tag>
docker-compose build
docker-compose up -d
```
