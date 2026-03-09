# ACM Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Docker and Docker Compose installed
- OR: Python 3.11+ and Node.js 18+

### Option 1: Docker (Recommended)

```bash
# Clone and navigate
cd acm-system

# Start everything
docker-compose -f docker/docker-compose.yml up --build

# Access the dashboard
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

That's it! The system is now running.

### Option 2: Local Development

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

Access at `http://localhost:3000`

## First Steps

### 1. Add Test Data

Run the test script to populate the system:

```bash
cd backend
python test_simulation.py
```

This adds:
- 2 satellites
- 3 debris objects
- Runs collision detection
- Displays results

### 2. Use the Dashboard

Open `http://localhost:3000` and you'll see:

**Left Panel:**
- Collision alerts with severity levels
- Fuel status for all satellites

**Center:**
- 3D visualization of Earth, satellites, and debris
- Orbit trajectory lines
- Use mouse to rotate, zoom, pan

**Right Panel:**
- Maneuver timeline
- Auto-optimization button

### 3. Try the API

**Add a satellite:**
```bash
curl -X POST http://localhost:8000/api/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "object_id": "SAT-003",
    "type": "satellite",
    "position": [7100.0, 200.0, 100.0],
    "velocity": [0.1, 7.6, 0.05],
    "timestamp": "2026-03-09T12:00:00Z"
  }'
```

**Check for collisions:**
```bash
curl http://localhost:8000/api/collisions?hours_ahead=24
```

**Run simulation:**
```bash
curl -X POST http://localhost:8000/api/simulate/step \
  -H "Content-Type: application/json" \
  -d '{"simulation_time_step": 24.0}'
```

**Schedule a maneuver:**
```bash
curl -X POST http://localhost:8000/api/maneuver/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "satellite_id": "SAT-003",
    "maneuver_time": 2.5,
    "delta_v_vector": [0.0, 0.005, 0.001]
  }'
```

### 4. Explore the Dashboard

**Collision Alerts:**
- Red alerts = Critical (< 1 hour to collision)
- Yellow alerts = Warning (> 1 hour)
- Click to see details

**Fuel Panel:**
- Green = Healthy (> 50%)
- Yellow = Moderate (20-50%)
- Red = Low (< 20%)

**3D Viewer:**
- Green boxes = Safe satellites
- Red boxes (pulsing) = Satellites at risk
- Orange spheres = Debris
- Cyan lines = Predicted orbits

**Maneuver Timeline:**
1. Select a satellite from dropdown
2. Click "AUTO-OPTIMIZE MANEUVERS"
3. View scheduled maneuvers with fuel costs

## Common Tasks

### Monitor a Constellation

```bash
# Get system status
curl http://localhost:8000/api/telemetry/status

# List all satellites
curl http://localhost:8000/api/telemetry/satellites

# List all debris
curl http://localhost:8000/api/telemetry/debris
```

### Plan Collision Avoidance

```bash
# Detect collisions
curl http://localhost:8000/api/collisions?hours_ahead=24

# Auto-optimize maneuvers for a satellite
curl -X POST http://localhost:8000/api/maneuver/optimize/SAT-001

# View scheduled maneuvers
curl http://localhost:8000/api/maneuver/schedule/SAT-001
```

### Simulate Orbital Propagation

```bash
# Propagate a single orbit
curl -X POST http://localhost:8000/api/simulate/propagate \
  -H "Content-Type: application/json" \
  -d '{
    "position": [7000.0, 0.0, 0.0],
    "velocity": [0.0, 7.5, 0.0],
    "hours": 24
  }'
```

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.11+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 is free: `lsof -i :8000`

### Frontend won't start
- Check Node version: `node --version` (need 18+)
- Clear cache: `rm -rf node_modules && npm install`
- Check port 3000 is free

### Docker issues
- Check Docker is running: `docker ps`
- Rebuild containers: `docker-compose down && docker-compose up --build`
- Check logs: `docker-compose logs backend` or `docker-compose logs frontend`

### No data showing
- Run test script: `python backend/test_simulation.py`
- Check API is responding: `curl http://localhost:8000/health`
- Check browser console for errors (F12)

## Next Steps

1. Read [FEATURES.md](FEATURES.md) for detailed capabilities
2. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for all endpoints
3. Review [PHYSICS_REFERENCE.md](PHYSICS_REFERENCE.md) for orbital mechanics
4. See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment

## Support

For issues or questions:
1. Check the documentation files
2. Review API docs at `http://localhost:8000/docs`
3. Check logs for error messages
4. Verify all dependencies are installed

Happy constellation managing! 🛰️
