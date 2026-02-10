# Deployment Guide

## Option 1: Render.com (Easiest)

### Prerequisites
- GitHub account
- Render account (free tier available)

### Steps

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/ecommerce_analytics.git
git push -u origin main
```

2. **Create Render services**

Go to [render.com](https://render.com) and create:

**A) Redis Service**
- Type: Redis
- Name: `recsys-redis`
- Plan: Free

**B) Web Service**
- Type: Web Service
- Connect your GitHub repo
- Environment: Docker
- Build Command: (auto-detected from Dockerfile)
- Start Command: (auto-detected)
- Plan: Starter ($7/month) or Free

**C) Environment Variables**
Add to web service:
```
REDIS_HOST=<your-redis-internal-url>
REDIS_PORT=6379
ARTIFACTS_PATH=/app/src/artifacts
```

3. **Deploy**
Render auto-deploys on every push to `main`.

---

## Option 2: Fly.io

### Prerequisites
- Fly.io account
- flyctl CLI installed

### Steps

1. **Install flyctl**
```bash
curl -L https://fly.io/install.sh | sh
```

2. **Login**
```bash
fly auth login
```

3. **Launch app**
```bash
fly launch
# Follow prompts:
# - Name your app
# - Choose region
# - Don't deploy yet
```

4. **Create Redis**
```bash
fly redis create
# Note the connection URL
```

5. **Set secrets**
```bash
fly secrets set REDIS_HOST=<your-redis-host>
fly secrets set REDIS_PORT=6379
```

6. **Deploy**
```bash
fly deploy
```

7. **Check status**
```bash
fly status
fly logs
```

---

## Option 3: Railway

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Login & Initialize**
```bash
railway login
railway init
```

3. **Add Redis**
```bash
railway add redis
```

4. **Deploy**
```bash
railway up
```

---

## Option 4: AWS ECS (Production)

### Architecture
- ECS Fargate for API containers
- ElastiCache Redis for sessions
- Application Load Balancer
- ECR for Docker images
- CloudWatch for logs

### Prerequisites
- AWS account
- AWS CLI configured
- ECR repository created

### High-Level Steps

1. **Build and push image**
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker build -t ecommerce-recsys .
docker tag ecommerce-recsys:latest <account>.dkr.ecr.us-east-1.amazonaws.com/ecommerce-recsys:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/ecommerce-recsys:latest
```

2. **Create ECS cluster**
```bash
aws ecs create-cluster --cluster-name recsys-cluster
```

3. **Create task definition** (see `ecs-task-definition.json`)

4. **Create ElastiCache Redis cluster**

5. **Create ECS service with ALB**

6. **Configure auto-scaling**

(Full AWS deployment guide beyond scope of this README)

---

## Model Updates (Production)

### Strategy: Download on Startup

1. **Train new model**
```bash
./train.sh
```

2. **Upload artifacts to S3**
```bash
aws s3 sync src/artifacts/ s3://your-bucket/models/2026-02-09/
```

3. **Update environment variable**
```bash
# On Render
MODEL_VERSION=2026-02-09
MODEL_S3_BUCKET=your-bucket

# Modify main.py to download from S3 on startup
```

4. **Restart service**
New containers will download updated model automatically.

---

## CI/CD Setup

Already configured in `.github/workflows/ci.yml`

### What it does:
1. Runs tests on every push
2. Builds Docker image on merge to `main`
3. Deploys to production (configure deploy hook)

### Add deployment hook:

**For Render:**
1. Go to your service → Settings → Deploy Hook
2. Copy the webhook URL
3. Add to GitHub Secrets: `RENDER_DEPLOY_HOOK`
4. Uncomment deploy step in `ci.yml`

**For Fly.io:**
```yaml
# In .github/workflows/ci.yml
- name: Deploy to Fly.io
  run: |
    flyctl deploy --remote-only
  env:
    FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

---

## Monitoring

### Health Checks
All platforms support health check endpoint:
```
GET /health
```

Configure:
- **Render**: Auto-detected
- **Fly.io**: In `fly.toml`
- **AWS**: In ALB target group

### Logs
- **Render**: Dashboard → Logs tab
- **Fly.io**: `fly logs`
- **AWS**: CloudWatch Logs

### Metrics (Future)
Add Prometheus metrics:
```python
from prometheus_client import Counter, Histogram

request_count = Counter('api_requests_total', 'Total requests')
latency = Histogram('recommendation_latency_seconds', 'Latency')
```

Expose on `/metrics` endpoint.

---

## Rollback

### Render
Dashboard → Deploy tab → Redeploy previous version

### Fly.io
```bash
fly releases
fly releases rollback <version>
```

### AWS ECS
Update service to previous task definition revision.

---

## Cost Estimates

| Platform | API + Redis | Notes |
|----------|-------------|-------|
| **Render** | $7-15/month | Starter tier + Redis |
| **Fly.io** | $5-10/month | Pay per usage |
| **Railway** | $5-20/month | Usage-based |
| **AWS ECS** | $30-100/month | Fargate + ElastiCache + ALB |

Start with Render or Fly.io, scale to AWS when needed.
