# ACM System - Complete Run Guide

## 🚀 Quick Start (Recommended)

### Option 1: Docker Compose (Easiest - One Command)

```bash
# Navigate to project directory
cd acm-system

# Start everything (backend + frontend)
docker-compose -f docker/docker-compose.yml up --build

# Access the application:
# - Frontend Dashboard: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
```

**To stop:**
```bash
# Press Ctrl+C, then:
docker-compose -f docker/docker-compose.yml down
```

---

## 🔧 Option 2: Local Development (Manual Setup)

### Prerequisites

**Required:**
- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn

**Check versions:**
```bash
python --version    # Should be 3.11+
node --version      # Should be 18+
npm --version
```

### Step 1: Start Backend

**Terminal 1 - Backend:**
```bash
# Navigate to backend directory
cd acm-system/backend

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Server will start at: http://localhost:8000
# API docs available at: http://localhost:8000/docs
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 2: Start Frontend

**Terminal 2 - Frontend:**
```bash
# Navigate to frontend directory
cd acm-system/frontend

# Install Node dependencies
npm install

# Start development server
npm run dev

# Server will start at: http://localhost:3000
```

**Expected output:**
```
VITE v5.0.0  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
➜  press h to show help
```

### Step 3: Test the System

**Terminal 3 - Test Data:**
```bash
# Navigate to backend directory
cd acm-system/backend

# Run test simulation to populate data
python test_simulation.py
```

**Expected output:**
```
================================================================================
ACM Orbital Physics Simulation Test
================================================================================

1. Adding test satellites...
   Added SAT-001: 200
   Added SAT-002: 200

2. Adding test debris objects...
   Added DEB-001: 200
   Added DEB-002: 200
   Added DEB-003: 200

3. Running orbital physics simulation...
   ✓ Simulation completed successfully
   ...
```

---

## 🐳 Option 3: Docker (Individual Containers)

### Backend Only

```bash
cd acm-system

# Build backend image
docker build -f docker/Dockerfile -t acm-backend .

# Run backend container
docker run -p 8000:8000 acm-backend

# Access at: http://localhost:8000
```

### Frontend Only

```bash
cd acm-system/frontend

# Build frontend image
docker build -t acm-frontend .

# Run frontend container
docker run -p 3000:80 acm-frontend

# Access at: http://localhost:3000
```

---

## 📊 Verify Installation

### 1. Check Backend Health

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}

# Check API version
curl http://localhost:8000/

# Expected response:
# {"status":"ACM System Online","version":"2.1.0","features":["AI Optimization","Real-time Visualization","Genetic Algorithms"]}
```

### 2. Check Frontend

Open browser and navigate to:
```
http://localhost:3000
```

You should see:
- ✅ "ACM MISSION CONTROL" header
- ✅ 3D Earth visualization in center
- ✅ Collision Alerts panel (left)
- ✅ Fuel Panel (left)
- ✅ Maneuver Timeline (right)

### 3. Test API Endpoints

```bash
# Get system status
curl http://localhost:8000/api/telemetry/status

# Add a test satellite
curl -X POST http://localhost:8000/api/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "object_id": "TEST-SAT",
    "type": "satellite",
    "position": [7000.0, 0.0, 0.0],
    "velocity": [0.0, 7.5, 0.0],
    "timestamp": "2026-03-09T12:00:00Z"
  }'

# Check AI optimizer status
curl http://localhost:8000/api/ai/status
```

---

## 🎮 Using the Dashboard

### 1. Add Test Data

Run the test script to populate the system:
```bash
cd acm-system/backend
python test_simulation.py
```

### 2. View 3D Visualization

- **Rotate**: Left-click and drag
- **Zoom**: Scroll wheel
- **Pan**: Right-click and drag

### 3. Monitor Collisions

- Check the **Collision Alerts** panel (left side)
- Red alerts = Critical (< 1 hour)
- Yellow alerts = Warning (> 1 hour)

### 4. Optimize Maneuvers

1. Select a satellite from the **Maneuver Timeline** dropdown (right side)
2. Click **"⚡ STANDARD OPTIMIZE"** for heuristic optimization
3. Click **"🧠 AI OPTIMIZE (GA)"** for AI-powered genetic algorithm optimization
4. View scheduled maneuvers with fuel costs

### 5. Monitor Fuel

- Check **Fuel Panel** (left side)
- Green = Healthy (> 50%)
- Yellow = Moderate (20-50%)
- Red = Low (< 20%)

---

## 🧪 Testing Features

### Test Collision Detection

```bash
curl -X POST http://localhost:8000/api/simulate/step \
  -H "Content-Type: application/json" \
  -d '{"simulation_time_step": 24.0}'
```

### Test AI Optimization

```bash
# Optimize single satellite
curl -X POST http://localhost:8000/api/ai/optimize/SAT-001

# Optimize entire fleet
curl -X POST http://localhost:8000/api/ai/optimize-fleet
```

### Test Maneuver Scheduling

```bash
curl -X POST http://localhost:8000/api/maneuver/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "satellite_id": "SAT-001",
    "maneuver_time": 2.5,
    "delta_v_vector": [0.0, 0.005, 0.001]
  }'
```

---

## 🐛 Troubleshooting

### Backend Issues

**Problem: Port 8000 already in use**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**Problem: Module not found**
```bash
cd acm-system/backend
pip install -r requirements.txt --force-reinstall
```

**Problem: Import errors**
```bash
# Make sure you're in the backend directory
cd acm-system/backend
python -c "import fastapi; print('FastAPI OK')"
python -c "import numpy; print('NumPy OK')"
python -c "import scipy; print('SciPy OK')"
```

### Frontend Issues

**Problem: Port 3000 already in use**
```bash
# Change port in vite.config.js or kill process
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

**Problem: Dependencies not installing**
```bash
cd acm-system/frontend
rm -rf node_modules package-lock.json
npm install
```

**Problem: Build errors**
```bash
cd acm-system/frontend
npm run build
# Check for errors in output
```

### Docker Issues

**Problem: Docker daemon not running**
```bash
# Start Docker Desktop (Windows/Mac)
# Or start Docker service (Linux)
sudo systemctl start docker
```

**Problem: Port conflicts**
```bash
# Stop all containers
docker-compose -f docker/docker-compose.yml down

# Remove all containers
docker rm -f $(docker ps -aq)

# Restart
docker-compose -f docker/docker-compose.yml up --build
```

**Problem: Build fails**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose -f docker/docker-compose.yml build --no-cache
docker-compose -f docker/docker-compose.yml up
```

### Browser Issues

**Problem: 3D visualization not loading**
- Check browser console (F12) for errors
- Ensure WebGL is enabled
- Try different browser (Chrome recommended)
- Update graphics drivers

**Problem: API calls failing**
- Check backend is running: `curl http://localhost:8000/health`
- Check browser console for CORS errors
- Verify proxy configuration in `vite.config.js`

---

## 📝 Environment Variables

### Backend (Optional)

Create `.env` file in `backend/` directory:
```bash
# Optional configurations
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
```

### Frontend (Optional)

Create `.env` file in `frontend/` directory:
```bash
# API endpoint (if different from default)
VITE_API_URL=http://localhost:8000
```

---

## 🔄 Development Workflow

### Hot Reload Development

**Backend:**
```bash
cd acm-system/backend
uvicorn main:app --reload
# Changes to .py files will auto-reload
```

**Frontend:**
```bash
cd acm-system/frontend
npm run dev
# Changes to .jsx files will auto-reload
```

### Production Build

**Backend:**
```bash
cd acm-system/backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend:**
```bash
cd acm-system/frontend
npm run build
# Output in dist/ directory
npm run preview  # Preview production build
```

---

## 📦 Dependencies

### Backend Requirements
```
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
numpy==1.26.3
scipy==1.12.0
python-multipart==0.0.6
requests==2.31.0
```

### Frontend Requirements
```
react@18.2.0
react-dom@18.2.0
three@0.159.0
@react-three/fiber@8.15.0
@react-three/drei@9.92.0
axios@1.6.0
tailwindcss@3.3.6
vite@5.0.0
```

---

## 🎯 Quick Command Reference

```bash
# Docker Compose (Recommended)
docker-compose -f docker/docker-compose.yml up --build

# Local Backend
cd acm-system/backend && uvicorn main:app --reload

# Local Frontend
cd acm-system/frontend && npm run dev

# Test Data
cd acm-system/backend && python test_simulation.py

# Health Check
curl http://localhost:8000/health

# API Docs
open http://localhost:8000/docs

# Dashboard
open http://localhost:3000
```

---

## 📚 Additional Resources

- **README.md** - Project overview and features
- **QUICKSTART.md** - 5-minute setup guide
- **API_DOCUMENTATION.md** - Complete API reference
- **AI_OPTIMIZATION.md** - AI algorithm details
- **VISUALIZATION_GUIDE.md** - 3D visualization reference
- **DEPLOYMENT.md** - Production deployment guide

---

## 🆘 Getting Help

1. Check logs for errors
2. Review troubleshooting section above
3. Verify all prerequisites are installed
4. Check API documentation at http://localhost:8000/docs
5. Review browser console (F12) for frontend errors

---

## ✅ Success Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Health check returns `{"status":"healthy"}`
- [ ] Dashboard loads with 3D visualization
- [ ] Test data populated successfully
- [ ] Can see satellites and debris in 3D view
- [ ] Collision alerts panel shows data
- [ ] Fuel panel displays satellite fuel levels
- [ ] Maneuver timeline allows satellite selection
- [ ] AI optimization button works

**If all checked, you're ready to go! 🚀**
