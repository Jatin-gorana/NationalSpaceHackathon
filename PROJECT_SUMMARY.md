# Autonomous Constellation Manager (ACM) - Project Summary

## 🎯 Project Overview

The **Autonomous Constellation Manager (ACM)** is an AI-powered satellite collision avoidance and orbital management system designed for monitoring 50+ satellites and thousands of debris objects in real-time.

## 🚀 Quick Start Commands

### Easiest Way (Docker Compose - Recommended)

```bash
cd acm-system
docker-compose -f docker/docker-compose.yml up --build
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

**Terminal 1 - Backend:**
```bash
cd acm-system/backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd acm-system/frontend
npm install
npm run dev
```

**Terminal 3 - Test Data:**
```bash
cd acm-system/backend
python test_simulation.py
```

## 📁 Project Structure

```
acm-system/
├── backend/                    # Python FastAPI Backend
│   ├── api/                   # API endpoints
│   │   ├── telemetry_api.py
│   │   ├── maneuver_api.py
│   │   ├── simulation_api.py
│   │   ├── maneuver_schedule_api.py
│   │   └── ai_optimization_api.py
│   ├── models/                # Data models
│   │   ├── satellite.py
│   │   └── debris.py
│   ├── services/              # Business logic
│   │   ├── telemetry_service.py
│   │   ├── propagation_engine.py
│   │   ├── collision_detector.py
│   │   ├── maneuver_planner.py
│   │   └── ai_optimizer.py
│   ├── utils/                 # Utilities
│   │   ├── constants.py
│   │   ├── orbital_math.py
│   │   └── fuel_model.py
│   ├── main.py               # FastAPI app
│   ├── requirements.txt      # Python dependencies
│   └── test_simulation.py    # Test script
│
├── frontend/                  # React + Three.js Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── SatelliteViewer.jsx
│   │   │   ├── CollisionAlerts.jsx
│   │   │   ├── FuelPanel.jsx
│   │   │   ├── ManeuverTimeline.jsx
│   │   │   └── SystemStatus.jsx
│   │   ├── api/acmApi.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── Documentation/
    ├── README.md
    ├── RUN_PROJECT.md
    ├── QUICKSTART.md
    ├── API_DOCUMENTATION.md
    ├── AI_OPTIMIZATION.md
    └── VISUALIZATION_GUIDE.md
```

## 🎨 Key Features

### Backend
✅ Real-time telemetry ingestion
✅ RK4 orbital propagation (10s timestep)
✅ KDTree collision detection (O(N log N))
✅ AI-powered maneuver optimization (Genetic Algorithms)
✅ Fuel consumption tracking
✅ Automated collision avoidance

### Frontend
✅ Real-time 3D visualization
✅ Dynamic orbit prediction
✅ Collision warning display
✅ Fuel monitoring
✅ AI optimization interface
✅ Maneuver timeline

## 🔧 Technology Stack

**Backend:** Python, FastAPI, NumPy, SciPy
**Frontend:** React, Three.js, Tailwind CSS
**Deployment:** Docker, Docker Compose

## 📚 Documentation

- **RUN_PROJECT.md** - Complete setup instructions
- **QUICKSTART.md** - 5-minute quick start
- **API_DOCUMENTATION.md** - API reference
- **AI_OPTIMIZATION.md** - AI algorithm details
- **VISUALIZATION_GUIDE.md** - 3D visualization guide

## 🚀 Getting Started

See [RUN_PROJECT.md](RUN_PROJECT.md) for complete instructions.

**Quick command:**
```bash
docker-compose -f docker/docker-compose.yml up --build
```

Then open http://localhost:3000
