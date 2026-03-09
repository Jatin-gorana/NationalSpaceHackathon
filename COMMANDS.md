# ACM System - Command Reference

## 🚀 Quick Start

```bash
# One-command start (Docker Compose)
cd acm-system
docker-compose -f docker/docker-compose.yml up --build

# Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🐳 Docker Commands

```bash
# Start everything
docker-compose -f docker/docker-compose.yml up --build

# Start in background
docker-compose -f docker/docker-compose.yml up -d

# Stop everything
docker-compose -f docker/docker-compose.yml down

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Rebuild from scratch
docker-compose -f docker/docker-compose.yml build --no-cache
docker-compose -f docker/docker-compose.yml up

# Remove all containers and volumes
docker-compose -f docker/docker-compose.yml down -v
```

## 💻 Local Development

### Backend

```bash
# Navigate to backend
cd acm-system/backend

# Install dependencies
pip install -r requirements.txt

# Start server (development)
uvicorn main:app --reload

# Start server (production)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Run tests
python test_simulation.py
```

### Frontend

```bash
# Navigate to frontend
cd acm-system/frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🧪 Testing Commands

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# System version
curl http://localhost:8000/

# System status
curl http://localhost:8000/api/telemetry/status

# AI optimizer status
curl http://localhost:8000/api/ai/status
```

### Add Test Data

```bash
# Run test simulation
cd acm-system/backend
python test_simulation.py

# Add single satellite
curl -X POST http://localhost:8000/api/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "object_id": "SAT-001",
    "type": "satellite",
    "position": [7000.0, 0.0, 0.0],
    "velocity": [0.0, 7.5, 0.0],
    "timestamp": "2026-03-09T12:00:00Z"
  }'

# Add debris
curl -X POST http://localhost:8000/api/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "object_id": "DEB-001",
    "type": "debris",
    "position": [7000.0, 50.0, 10.0],
    "velocity": [0.05, 7.48, 0.01],
    "timestamp": "2026-03-09T12:00:00Z"
  }'
```

### Query Data

```bash
# Get all satellites
curl http://localhost:8000/api/telemetry/satellites

# Get all debris
curl http://localhost:8000/api/telemetry/debris

# Get system status
curl http://localhost:8000/api/telemetry/status
```

## 🎯 Collision Detection

```bash
# Detect collisions (24 hours)
curl http://localhost:8000/api/collisions?hours_ahead=24

# Run full simulation
curl -X POST http://localhost:8000/api/simulate/step \
  -H "Content-Type: application/json" \
  -d '{"simulation_time_step": 24.0}'

# Propagate single orbit
curl -X POST http://localhost:8000/api/simulate/propagate \
  -H "Content-Type: application/json" \
  -d '{
    "position": [7000.0, 0.0, 0.0],
    "velocity": [0.0, 7.5, 0.0],
    "hours": 24
  }'
```

## 🚀 Maneuver Planning

```bash
# Standard optimization
curl -X POST http://localhost:8000/api/maneuver/optimize/SAT-001

# Schedule manual maneuver
curl -X POST http://localhost:8000/api/maneuver/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "satellite_id": "SAT-001",
    "maneuver_time": 2.5,
    "delta_v_vector": [0.0, 0.005, 0.001]
  }'

# Get scheduled maneuvers
curl http://localhost:8000/api/maneuver/schedule/SAT-001

# Plan for all satellites
curl http://localhost:8000/api/maneuvers/all
```

## 🧠 AI Optimization

```bash
# AI optimize single satellite
curl -X POST http://localhost:8000/api/ai/optimize/SAT-001

# AI optimize with custom parameters
curl -X POST http://localhost:8000/api/ai/optimize/SAT-001 \
  -H "Content-Type: application/json" \
  -d '{
    "satellite_id": "SAT-001",
    "population_size": 100,
    "generations": 200
  }'

# AI optimize entire fleet
curl -X POST http://localhost:8000/api/ai/optimize-fleet

# Get AI optimizer status
curl http://localhost:8000/api/ai/status
```

## 🔧 Troubleshooting

### Kill Processes

```bash
# Windows - Kill port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Windows - Kill port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac - Kill port 8000
lsof -ti:8000 | xargs kill -9

# Linux/Mac - Kill port 3000
lsof -ti:3000 | xargs kill -9
```

### Clean Install

```bash
# Backend
cd acm-system/backend
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Frontend
cd acm-system/frontend
rm -rf node_modules package-lock.json
npm install

# Docker
docker system prune -a
docker-compose -f docker/docker-compose.yml build --no-cache
```

### Check Versions

```bash
# Python
python --version

# Node
node --version

# npm
npm --version

# Docker
docker --version
docker-compose --version
```

## 📊 Monitoring

```bash
# Watch backend logs
cd acm-system/backend
uvicorn main:app --reload --log-level debug

# Watch Docker logs
docker-compose -f docker/docker-compose.yml logs -f

# Watch specific service
docker-compose -f docker/docker-compose.yml logs -f backend
docker-compose -f docker/docker-compose.yml logs -f frontend
```

## 🌐 Browser Commands

```bash
# Open dashboard
open http://localhost:3000

# Open API docs
open http://localhost:8000/docs

# Open alternative API docs
open http://localhost:8000/redoc
```

## 📦 Build Commands

```bash
# Build backend Docker image
docker build -f docker/Dockerfile -t acm-backend .

# Build frontend Docker image
cd frontend
docker build -t acm-frontend .

# Build with Docker Compose
docker-compose -f docker/docker-compose.yml build
```

## 🔄 Git Commands

```bash
# Check status
git status

# Add all changes
git add .

# Commit
git commit -m "Your message"

# Push to remote
git push origin main

# Pull latest
git pull origin main
```

## 📝 Development Helpers

```bash
# Format Python code
cd acm-system/backend
black .

# Lint Python code
pylint **/*.py

# Format JavaScript
cd acm-system/frontend
npm run format

# Lint JavaScript
npm run lint
```

## 🎮 Interactive API Testing

```bash
# Open interactive API docs
open http://localhost:8000/docs

# Or use curl with pretty print
curl http://localhost:8000/api/telemetry/status | python -m json.tool

# Or use httpie (if installed)
http http://localhost:8000/api/telemetry/status
```

## 📈 Performance Testing

```bash
# Benchmark collision detection
time curl -X POST http://localhost:8000/api/simulate/step \
  -H "Content-Type: application/json" \
  -d '{"simulation_time_step": 24.0}'

# Benchmark AI optimization
time curl -X POST http://localhost:8000/api/ai/optimize/SAT-001
```

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Start everything | `docker-compose -f docker/docker-compose.yml up --build` |
| Stop everything | `docker-compose -f docker/docker-compose.yml down` |
| Backend only | `cd backend && uvicorn main:app --reload` |
| Frontend only | `cd frontend && npm run dev` |
| Test data | `cd backend && python test_simulation.py` |
| Health check | `curl http://localhost:8000/health` |
| View logs | `docker-compose -f docker/docker-compose.yml logs -f` |
| Clean Docker | `docker system prune -a` |

## 🆘 Emergency Commands

```bash
# Stop all Docker containers
docker stop $(docker ps -aq)

# Remove all Docker containers
docker rm $(docker ps -aq)

# Remove all Docker images
docker rmi $(docker images -q)

# Kill all Python processes
pkill -9 python

# Kill all Node processes
pkill -9 node

# Reset everything
docker-compose -f docker/docker-compose.yml down -v
docker system prune -a -f
```

---

**Pro Tip:** Bookmark this file for quick command reference! 📌
