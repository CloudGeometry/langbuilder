# Deployment Topology - LangBuilder

## Overview

This document describes the deployment architecture for LangBuilder, including Docker configurations, environment setup, service ports, and scaling considerations.

## Deployment Diagram

```mermaid
graph TB
    subgraph Internet
        Users[Users/Clients]
    end

    subgraph LoadBalancer["Load Balancer (Traefik)"]
        Traefik[Traefik v3.0]
    end

    subgraph FrontendTier["Frontend Tier"]
        FE1[Frontend Container]
        FE2[Frontend Container]
    end

    subgraph BackendTier["Backend Tier"]
        BE1[Backend API]
        BE2[Backend API]
    end

    subgraph WorkerTier["Worker Tier"]
        W1[Celery Worker]
        W2[Celery Worker]
        Flower[Flower Monitor]
    end

    subgraph DataTier["Data Tier"]
        PG[(PostgreSQL)]
        Redis[(Redis)]
        RabbitMQ[(RabbitMQ)]
    end

    subgraph Monitoring["Monitoring"]
        Prometheus[Prometheus]
        Grafana[Grafana]
    end

    Users --> Traefik
    Traefik --> FE1 & FE2
    Traefik --> BE1 & BE2
    Traefik --> Prometheus
    Traefik --> Grafana

    FE1 & FE2 --> BE1 & BE2
    BE1 & BE2 --> PG
    BE1 & BE2 --> Redis
    BE1 & BE2 --> RabbitMQ

    W1 & W2 --> PG
    W1 & W2 --> Redis
    W1 & W2 --> RabbitMQ
    Flower --> RabbitMQ

    Prometheus --> BE1 & BE2
    Prometheus --> W1 & W2
```

## Deployment Options

### 1. Development (Local)

Single-process development setup for local development and testing.

```
┌─────────────────────────────────────────┐
│           Development Machine           │
│                                         │
│  ┌─────────────┐    ┌──────────────┐   │
│  │   Vite Dev  │    │   Uvicorn    │   │
│  │   Server    │    │   (reload)   │   │
│  │   :5175     │    │    :8002     │   │
│  └─────────────┘    └──────────────┘   │
│                            │            │
│                     ┌──────┴──────┐    │
│                     │   SQLite    │    │
│                     │  (file DB)  │    │
│                     └─────────────┘    │
└─────────────────────────────────────────┘
```

**Start Commands**:
```bash
# Backend
cd langbuilder
uv run langbuilder run

# Frontend (separate terminal)
cd langbuilder/src/frontend
npm run dev
```

### 2. Docker Compose (Staging)

Full containerized deployment suitable for staging and small production.

```yaml
# docker-compose.yml structure
services:
  frontend:      # React app (nginx)
  backend:       # FastAPI app
  db:            # PostgreSQL
  redis:         # Cache/broker
  rabbitmq:      # Message queue
  celeryworker:  # Background worker
  flower:        # Celery monitor
```

**Deployment**:
```bash
cd langbuilder/deploy
docker-compose up -d
```

### 3. Docker Swarm (Production)

Orchestrated deployment with Traefik for load balancing and TLS.

```yaml
# Production docker-compose.yml includes:
services:
  proxy:         # Traefik load balancer
  frontend:      # React app (replicated)
  backend:       # FastAPI (replicated)
  db:            # PostgreSQL (persistent)
  redis:         # Redis (persistent)
  rabbitmq:      # RabbitMQ (persistent)
  celeryworker:  # Workers (scalable)
  flower:        # Celery monitor
  prometheus:    # Metrics
  grafana:       # Dashboards
  pgadmin:       # DB admin
```

## Service Configuration

### Service Ports

| Service | Internal Port | External Port | Protocol |
|---------|--------------|---------------|----------|
| Frontend | 80 | 80/443 | HTTP/HTTPS |
| Backend API | 7860 | - (via proxy) | HTTP |
| PostgreSQL | 5432 | 5432 | TCP |
| Redis | 6379 | 6379 | TCP |
| RabbitMQ | 5672 | 5672 | AMQP |
| RabbitMQ Mgmt | 15672 | 15672 | HTTP |
| Flower | 5555 | 5555 | HTTP |
| Prometheus | 9090 | 9090 | HTTP |
| Grafana | 3000 | 3000 | HTTP |
| PgAdmin | 5050 | - (via proxy) | HTTP |

### Environment Variables

**Backend Configuration**:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/langbuilder
SQLMODEL_MIGRATE_URL=postgresql://user:pass@db:5432/langbuilder

# Redis
REDIS_URL=redis://redis:6379/0

# RabbitMQ
BROKER_URL=amqp://admin:admin@broker:5672//

# Application
BACKEND_PORT=7860
SECRET_KEY=<generated-secret>
LANGBUILDER_AUTO_LOGIN=false
LANGBUILDER_SUPERUSER=admin@example.com
LANGBUILDER_SUPERUSER_PASSWORD=<password>

# LLM Providers (optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Frontend Configuration**:
```bash
# API URL
VITE_BACKEND_URL=https://api.example.com
```

**Traefik Configuration**:
```bash
DOMAIN=langbuilder.example.com
TRAEFIK_PUBLIC_NETWORK=traefik-public
TRAEFIK_TAG=langbuilder
STACK_NAME=langbuilder
```

## Container Images

### Backend Image

**Dockerfile**: `langbuilder/deploy/Dockerfile`

```dockerfile
FROM python:3.11-slim

# Install dependencies
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync

# Copy application
COPY langbuilder/ ./langbuilder/

# Run
EXPOSE 7860
CMD ["uvicorn", "langbuilder.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

**Image**: `cloudgeometry/langbuilder-backend:latest`

### Frontend Image

**Multi-stage build**:
```dockerfile
# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

**Image**: `cloudgeometry/langbuilder-frontend:latest`

## Traefik Routing

### Route Configuration

```yaml
# Backend routes
- traefik.http.routers.backend.rule=PathPrefix(`/api/v1`) || PathPrefix(`/api/v2`) || PathPrefix(`/docs`) || PathPrefix(`/health`)

# Frontend routes (catch-all)
- traefik.http.routers.frontend.rule=PathPrefix(`/`)

# Admin routes
- traefik.http.routers.pgadmin.rule=Host(`pgadmin.${DOMAIN}`)
- traefik.http.routers.flower.rule=Host(`flower.${DOMAIN}`)
- traefik.http.routers.grafana.rule=PathPrefix(`/grafana`)
```

### TLS Configuration

```yaml
# Let's Encrypt automatic certificates
- traefik.http.routers.proxy-https.tls=true
- traefik.http.routers.proxy-https.tls.certresolver=le

# HTTP to HTTPS redirect
- traefik.http.middlewares.https-redirect.redirectscheme.scheme=https
```

## Scaling Considerations

### Horizontal Scaling

| Component | Scaling Strategy | Considerations |
|-----------|-----------------|----------------|
| **Frontend** | Replicas | Stateless, easy to scale |
| **Backend** | Replicas | Stateless, requires shared Redis |
| **Workers** | Replicas | Scale based on queue depth |
| **Database** | Read replicas | Write to primary only |
| **Redis** | Cluster | For high-availability |
| **RabbitMQ** | Cluster | For message persistence |

### Resource Requirements

**Minimum (Development)**:
| Component | CPU | Memory |
|-----------|-----|--------|
| Backend | 0.5 | 512MB |
| Frontend | 0.25 | 256MB |
| Database | 0.5 | 512MB |
| Redis | 0.25 | 256MB |
| **Total** | 1.5 | 1.5GB |

**Recommended (Production)**:
| Component | CPU | Memory | Replicas |
|-----------|-----|--------|----------|
| Backend | 2 | 2GB | 2-4 |
| Frontend | 0.5 | 512MB | 2 |
| Workers | 2 | 2GB | 2-4 |
| Database | 4 | 4GB | 1 (+ replicas) |
| Redis | 1 | 1GB | 1 |
| RabbitMQ | 1 | 1GB | 1 |
| **Total** | 12+ | 12GB+ | - |

## Health Checks

### Backend Health Check

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:7860/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Database Health Check

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Redis Health Check

```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 5
```

## Persistent Volumes

```yaml
volumes:
  app-db-data:        # PostgreSQL data
  redis-data:         # Redis persistence
  rabbitmq_data:      # RabbitMQ state
  rabbitmq_log:       # RabbitMQ logs
  grafana_data:       # Grafana dashboards
  pgadmin-data:       # PgAdmin config
```

### Volume Backup Strategy

```bash
# PostgreSQL backup
docker exec db pg_dump -U postgres langbuilder > backup.sql

# Redis backup
docker exec redis redis-cli BGSAVE

# Full volume backup
docker run --rm -v app-db-data:/data -v $(pwd):/backup \
  alpine tar cvf /backup/db-backup.tar /data
```

## Deployment Checklist

### Pre-deployment

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates provisioned
- [ ] Secrets management configured
- [ ] Monitoring dashboards ready

### Post-deployment

- [ ] Health checks passing
- [ ] SSL certificate valid
- [ ] Database connectivity verified
- [ ] Worker queues processing
- [ ] Monitoring alerts configured

---

*Generated by CloudGeometry AIx SDLC - Architecture Documentation*
