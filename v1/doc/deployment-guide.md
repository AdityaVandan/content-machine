# Deployment Guide

## Overview

This guide covers deployment strategies for Content Machine in various environments, from development setups to production deployments.

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **Memory**: 4GB RAM
- **Storage**: 20GB available space
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2

### Recommended Requirements
- **CPU**: 4+ cores
- **Memory**: 8GB+ RAM
- **Storage**: 50GB+ SSD
- **Network**: Stable internet connection for LLM API calls

### Dependencies
- **Python**: 3.11+
- **Redis**: 6.0+
- **Docker**: 20.10+ (optional)
- **Docker Compose**: 2.0+ (optional)

## Environment Setup

### 1. Development Environment

#### Local Development Setup

```bash
# Clone repository
git clone <repository-url>
cd content-machine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env with your API keys
nano .env
```

#### Environment Variables

```bash
# Required
OPENROUTER_API_KEY=your_openrouter_api_key

# Platform APIs (optional, based on platforms used)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

MEDIUM_INTEGRATION_TOKEN=your_medium_integration_token

# Optional
DATABASE_URL=sqlite:///content_machine.db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Configuration
DEFAULT_LLM_MODEL=anthropic/claude-3-sonnet
HUMAN_REVIEW_REQUIRED=true
LOG_LEVEL=INFO
```

#### Database Initialization

```python
# Initialize database (run once)
python -c "
from src.core.database import create_tables
create_tables()
print('Database initialized successfully')
"
```

#### Starting Services

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery Worker
celery -A src.scheduler.tasks worker --loglevel=info

# Terminal 3: Start Celery Beat (Scheduler)
celery -A src.scheduler.tasks beat --loglevel=info

# Terminal 4: Start Web Server
python run.py
```

### 2. Docker Development Setup

#### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Docker Compose Configuration

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    volumes:
      - .:/app
      - content_machine_db:/app/data
    depends_on:
      - redis

  worker:
    build: .
    command: celery -A src.scheduler.tasks worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    volumes:
      - .:/app
      - content_machine_db:/app/data
    depends_on:
      - redis

  beat:
    build: .
    command: celery -A src.scheduler.tasks beat --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    volumes:
      - .:/app
      - content_machine_db:/app/data
    depends_on:
      - redis

  flower:
    build: .
    command: celery -A src.scheduler.tasks flower
    ports:
      - "5555:5555"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

volumes:
  redis_data:
  content_machine_db:
```

## Production Deployment

### 1. Production Environment Setup

#### Production Environment Variables

```bash
# Production configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Security
SECRET_KEY=your_super_secret_key_here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL recommended)
DATABASE_URL=postgresql://user:password@localhost:5432/content_machine

# Redis (with authentication)
REDIS_URL=redis://:password@localhost:6379/0

# Monitoring
SENTRY_DSN=your_sentry_dsn
PROMETHEUS_ENABLED=true
```

#### Production Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "web.api.main:app"]
```

### 2. Cloud Deployment

#### AWS Deployment

**EC2 Instance Setup:**

```bash
# Launch EC2 instance (t3.medium recommended)
# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and deploy
git clone <repository-url>
cd content-machine
docker-compose -f docker-compose.prod.yml up -d
```

**Production Docker Compose:**

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=content_machine
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/content_machine
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - postgres
      - redis

  worker:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A src.scheduler.tasks worker --loglevel=info --concurrency=4
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/content_machine
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - postgres
      - redis

  beat:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A src.scheduler.tasks beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/content_machine
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - postgres
      - redis

volumes:
  redis_data:
  postgres_data:
```

#### Google Cloud Platform

**Cloud Run Deployment:**

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT-ID/content-machine

# Deploy to Cloud Run
gcloud run deploy content-machine \
  --image gcr.io/PROJECT-ID/content-machine \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "OPENROUTER_API_KEY=$OPENROUTER_API_KEY"
```

#### Azure Container Instances

```bash
# Create resource group
az group create --name content-machine-rg --location eastus

# Deploy container
az container create \
  --resource-group content-machine-rg \
  --name content-machine \
  --image your-registry/content-machine:latest \
  --ports 8000 \
  --environment-variables \
    OPENROUTER_API_KEY=$OPENROUTER_API_KEY
```

### 3. Kubernetes Deployment

#### Kubernetes Manifests

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: content-machine

---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: content-machine-config
  namespace: content-machine
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"

---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: content-machine-secrets
  namespace: content-machine
type: Opaque
data:
  OPENROUTER_API_KEY: <base64-encoded-key>
  DATABASE_URL: <base64-encoded-url>

---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: content-machine-web
  namespace: content-machine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: content-machine-web
  template:
    metadata:
      labels:
        app: content-machine-web
    spec:
      containers:
      - name: web
        image: content-machine:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: content-machine-config
        - secretRef:
            name: content-machine-secrets

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: content-machine-service
  namespace: content-machine
spec:
  selector:
    app: content-machine-web
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Monitoring and Logging

### 1. Application Monitoring

#### Prometheus Metrics

```python
# Add to web/api/main.py
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

#### Health Checks

```python
# Enhanced health check
@app.get("/health")
async def health_check():
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "llm": await check_llm_connection()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        content={
            "status": "healthy" if all_healthy else "unhealthy",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        },
        status_code=status_code
    )
```

### 2. Log Management

#### Structured Logging Configuration

```python
# src/core/logging.py
import structlog
import logging
import sys

def configure_logging(log_level: str = "INFO"):
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
```

### 3. Error Tracking

#### Sentry Integration

```python
# Add to requirements.txt
sentry-sdk[fastapi]

# Add to web/api/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "development")
)
```

## Security Considerations

### 1. API Security

#### Rate Limiting

```python
# Add to web/api/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.post("/content/create")
@limiter.limit("10/minute")
async def create_content(request: Request, ...):
    # Existing implementation
```

#### Input Validation

```python
# Enhanced validation
from pydantic import validator, constr

class ContentRequest(BaseModel):
    topic: constr(min_length=1, max_length=200)
    keywords: List[constr(max_length=50)] = Field(default_factory=list, max_items=10)
    
    @validator('topic')
    def validate_topic(cls, v):
        if any profanity in v.lower():
            raise ValueError('Topic contains inappropriate content')
        return v
```

### 2. Infrastructure Security

#### SSL/TLS Configuration

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Backup and Recovery

### 1. Database Backups

```bash
# PostgreSQL backup script
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="content_machine"

pg_dump $DB_NAME > "$BACKUP_DIR/content_machine_$TIMESTAMP.sql"

# Keep last 7 days of backups
find $BACKUP_DIR -name "content_machine_*.sql" -mtime +7 -delete
```

### 2. Redis Backups

```bash
# Redis backup script
#!/bin/bash
REDIS_DIR="/var/lib/redis"
BACKUP_DIR="/backups/redis"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

redis-cli BGSAVE
cp $REDIS_DIR/dump.rdb "$BACKUP_DIR/dump_$TIMESTAMP.rdb"
```

## Performance Optimization

### 1. Caching Strategy

```python
# Redis caching for API responses
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_response(expire_time=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            
            return result
        return wrapper
    return decorator
```

### 2. Database Optimization

```python
# Database connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## Troubleshooting

### Common Issues

1. **Celery Tasks Not Running**
   ```bash
   # Check worker status
   celery -A src.scheduler.tasks inspect active
   
   # Check queue length
   celery -A src.scheduler.tasks inspect reserved
   ```

2. **Redis Connection Issues**
   ```bash
   # Test Redis connection
   redis-cli ping
   
   # Check Redis logs
   docker logs content-machine_redis_1
   ```

3. **Memory Issues**
   ```bash
   # Monitor memory usage
   docker stats
   
   # Adjust worker concurrency
   celery -A src.scheduler.tasks worker --concurrency=2
   ```

### Log Analysis

```bash
# View application logs
docker logs content-machine_web_1

# Filter error logs
docker logs content-machine_web_1 2>&1 | grep ERROR

# Monitor in real-time
docker logs -f content-machine_web_1
```

This deployment guide provides comprehensive instructions for setting up Content Machine in various environments, from development to production deployments.
