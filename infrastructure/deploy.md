# ForecastEngine Deployment Guide

## Quick Start

### Local Development
```bash
# Install dependencies
pip install -r infrastructure/requirements.prod.txt

# Run API
python -m uvicorn src.api.main:app --reload

# Run Dashboard (separate terminal)
streamlit run src/dashboard/app.py
```

### Docker Deployment

#### Single Container
```bash
# Build image
docker build -f infrastructure/Dockerfile -t forecastengine .

# Run API
docker run -p 8000:8000 -v $(pwd)/models:/app/models forecastengine

# Run Dashboard
docker run -p 8501:8501 forecastengine streamlit run src/dashboard/app.py --server.port=8501 --server.address=0.0.0.0
```

#### Full Stack with Docker Compose
```bash
cd infrastructure
docker-compose up -d
```

Services will be available at:
- API: http://localhost:8000
- Dashboard: http://localhost:8501
- API Docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090

### Production Deployment

#### AWS ECS
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -f infrastructure/Dockerfile -t forecastengine .
docker tag forecastengine:latest <account>.dkr.ecr.us-east-1.amazonaws.com/forecastengine:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/forecastengine:latest

# Deploy using ECS task definition
aws ecs update-service --cluster forecast-cluster --service forecast-service --force-new-deployment
```

#### Kubernetes
```bash
# Apply Kubernetes manifests
kubectl apply -f infrastructure/k8s/

# Check deployment
kubectl get pods -l app=forecastengine
kubectl get services
```

#### Google Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/forecastengine
gcloud run deploy --image gcr.io/PROJECT_ID/forecastengine --platform managed
```

### Environment Variables

Required:
- `PYTHONPATH=/app/src`
- `LOG_LEVEL=INFO`

Optional:
- `MODEL_REGISTRY_PATH=/app/models`
- `DATA_PATH=/app/data`
- `REDIS_URL=redis://redis:6379`

### Health Checks

- API Health: `GET /health`
- Metrics: `GET /metrics`
- Ready: `GET /ready`

### Monitoring

- Prometheus metrics at `/metrics`
- Logs in JSON format
- Health checks every 30s

### Scaling

#### Horizontal Scaling
```bash
# Docker Compose
docker-compose up --scale forecast-api=3

# Kubernetes
kubectl scale deployment forecastengine --replicas=3
```

#### Vertical Scaling
```yaml
# Update resource limits
resources:
  limits:
    memory: "2Gi"
    cpu: "1000m"
  requests:
    memory: "1Gi"
    cpu: "500m"
```

### Troubleshooting

#### Common Issues
1. **Port conflicts**: Change ports in docker-compose.yml
2. **Memory issues**: Increase container memory limits
3. **Model loading fails**: Check volume mounts and permissions

#### Logs
```bash
# Docker Compose logs
docker-compose logs -f forecast-api

# Kubernetes logs
kubectl logs -f deployment/forecastengine
```

### Security

#### Production Checklist
- [ ] Enable HTTPS/TLS
- [ ] Set up authentication
- [ ] Configure firewall rules
- [ ] Use secrets management
- [ ] Enable audit logging
- [ ] Regular security updates

#### Authentication
```python
# Add to API configuration
ENABLE_AUTH = True
JWT_SECRET_KEY = "your-secret-key"
```

### Backup & Recovery

#### Model Backup
```bash
# Backup models directory
tar -czf models-backup-$(date +%Y%m%d).tar.gz models/

# Restore models
tar -xzf models-backup-20240115.tar.gz
```

#### Database Backup (if using)
```bash
# PostgreSQL
pg_dump forecastdb > backup.sql

# Restore
psql forecastdb < backup.sql
```