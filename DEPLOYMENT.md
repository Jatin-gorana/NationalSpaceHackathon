# ACM Deployment Guide

## Quick Start with Docker Compose

The easiest way to run the complete ACM system (backend + frontend):

```bash
cd acm-system
docker-compose -f docker/docker-compose.yml up --build
```

Access the dashboard at: `http://localhost:3000`

API available at: `http://localhost:8000`

## Manual Deployment

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Production Deployment

### Backend (Docker)

```bash
cd acm-system
docker build -f docker/Dockerfile -t acm-backend .
docker run -p 8000:8000 acm-backend
```

### Frontend (Docker)

```bash
cd frontend
docker build -t acm-frontend .
docker run -p 80:80 acm-frontend
```

## Environment Variables

### Backend
- `PYTHONUNBUFFERED=1` - Enable Python output buffering

### Frontend
- API proxy configured in `vite.config.js` for development
- Nginx proxy configured in `nginx.conf` for production

## Architecture

```
┌─────────────────┐
│   Frontend      │
│  (React + 3JS)  │
│   Port: 3000    │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   Backend       │
│  (FastAPI)      │
│   Port: 8000    │
└─────────────────┘
```

## Health Checks

Backend: `http://localhost:8000/health`
Frontend: `http://localhost:3000`

## Scaling

For production deployments:
- Use Redis for shared state across backend instances
- Deploy multiple backend replicas behind load balancer
- Use CDN for frontend static assets
- Enable HTTPS with SSL certificates

## Monitoring

Monitor these endpoints:
- `/api/telemetry/status` - System health
- `/api/collisions` - Active threats
- `/health` - Backend health check
