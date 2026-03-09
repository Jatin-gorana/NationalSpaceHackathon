# Autonomous Constellation Manager (ACM)

Satellite collision avoidance and orbital management system with real-time 3D visualization for monitoring 50+ satellites and thousands of debris objects.

## Features

### Backend
- Real-time telemetry ingestion for satellites and debris
- 24-hour collision prediction using RK4 orbital propagation
- Earth-Centered Inertial (ECI) coordinate system
- High-precision 10-second timestep integration
- Optimized collision detection with KDTree spatial indexing (O(N log N))
- Time of Closest Approach (TCA) computation
- 50 km search radius with 100m collision threshold
- **AI-powered maneuver optimization using Genetic Algorithms**
- **Multi-objective fitness: collision avoidance + fuel minimization + slot maintenance**
- Fuel consumption tracking using Tsiolkovsky rocket equation
- Automated collision avoidance planning
- Station-keeping to maintain satellites within 10km of assigned slots
- Thruster cooldown management (3600s between burns)

### Frontend
- Futuristic 3D mission control dashboard
- **Real-time orbit prediction with RK4 integration in browser**
- **Dynamic orbit trajectory lines for all objects**
- **Collision warning visualization with dashed lines**
- Real-time Earth and satellite visualization with Three.js
- Enhanced satellite models with solar panels
- Debris field visualization with orbit paths
- Collision warning indicators with severity levels
- Fuel status monitoring for entire fleet
- Maneuver timeline with AI optimization button
- **AI vs Standard optimization comparison**
- Auto-optimization for collision avoidance
- Responsive design with Tailwind CSS

## Tech Stack

### Backend
- Python + FastAPI
- NumPy + SciPy
- KDTree spatial indexing
- RK4 orbital propagation
- Docker

### Frontend
- React 18
- Three.js + React Three Fiber
- Tailwind CSS
- Vite
- Axios

## Quick Start

### Full Stack with Docker Compose (Recommended)

```bash
cd acm-system
docker-compose -f docker/docker-compose.yml up --build
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### Local Development

#### Backend
```bash
cd acm-system/backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend
```bash
cd acm-system/frontend
npm install
npm run dev
```

## API Endpoints

### Telemetry
- `POST /api/telemetry` - Ingest satellite/debris telemetry
- `GET /api/telemetry/satellites` - Get all satellites
- `GET /api/telemetry/debris` - Get all debris
- `GET /api/telemetry/status` - System status

### Collision Detection & Maneuvers
- `GET /api/collisions?hours_ahead=24` - Detect collisions
- `POST /api/maneuvers/plan/{satellite_id}` - Plan maneuvers for satellite
- `GET /api/maneuvers/all` - Plan maneuvers for all satellites

### Maneuver Scheduling
- `POST /api/maneuver/schedule` - Schedule manual maneuver
- `GET /api/maneuver/schedule/{satellite_id}` - Get scheduled maneuvers
- `POST /api/maneuver/optimize/{satellite_id}` - Auto-optimize maneuvers

### AI Optimization
- `POST /api/ai/optimize/{satellite_id}` - AI-optimize using genetic algorithm
- `POST /api/ai/optimize-fleet` - AI-optimize entire fleet
- `GET /api/ai/status` - Get AI optimizer status and configuration

### Simulation
- `POST /api/simulate/propagate` - Propagate orbit trajectory
- `POST /api/simulate/predict` - Predict position at time
- `POST /api/simulate/step` - Run complete simulation with collision detection

## Example Usage

```bash
# Ingest satellite telemetry
curl -X POST http://localhost:8000/api/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "object_id": "SAT-001",
    "type": "satellite",
    "position": [7000.0, 0.0, 0.0],
    "velocity": [0.0, 7.5, 0.0],
    "timestamp": "2026-03-09T12:00:00Z"
  }'

# Detect collisions
curl http://localhost:8000/api/collisions?hours_ahead=24

# Plan maneuvers
curl -X POST http://localhost:8000/api/maneuvers/plan/SAT-001

# Run simulation step
curl -X POST http://localhost:8000/api/simulate/step \
  -H "Content-Type: application/json" \
  -d '{"simulation_time_step": 24.0}'

# Schedule a maneuver
curl -X POST http://localhost:8000/api/maneuver/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "satellite_id": "SAT-001",
    "maneuver_time": 2.5,
    "delta_v_vector": [0.0, 0.005, 0.001]
  }'

# Auto-optimize maneuvers
curl -X POST http://localhost:8000/api/maneuver/optimize/SAT-001

# AI-optimize with genetic algorithm
curl -X POST http://localhost:8000/api/ai/optimize/SAT-001

# AI-optimize entire fleet
curl -X POST http://localhost:8000/api/ai/optimize-fleet
```

## Physics Model

The system uses scientifically accurate orbital mechanics:

- Coordinate System: Earth-Centered Inertial (ECI)
- Integration Method: Runge-Kutta 4th order (RK4)
- Timestep: 10 seconds (high precision)
- Gravitational Model: d²r/dt² = -μr / |r|³
  - μ = 398600.4418 km³/s² (Earth's gravitational parameter)

## Collision Detection Algorithm

Optimized spatial indexing for efficient collision detection:

1. Propagate all objects using RK4 (10s timestep)
2. Build KDTree for debris positions at each timestep
3. Query satellites within 50 km search radius (O(N log N))
4. Compute Time of Closest Approach (TCA) for close pairs
5. Flag collisions if minimum distance < 100 meters

This approach avoids O(N²) brute-force checks and scales efficiently to thousands of objects.

## Testing

Run the test simulation:

```bash
cd backend
python test_simulation.py
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 3D Viewer    │  │ Collision    │  │ Fuel Panel   │  │
│  │ (Three.js)   │  │ Alerts       │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ Maneuver     │  │ System       │                    │
│  │ Timeline     │  │ Status       │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │              API Layer                            │  │
│  │  /telemetry  /collisions  /maneuvers  /simulate  │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │            Services Layer                         │  │
│  │  • Propagation Engine (RK4)                       │  │
│  │  • Collision Detector (KDTree)                    │  │
│  │  • Maneuver Planner (Optimization)                │  │
│  │  • Fuel Model (Rocket Equation)                   │  │
│  │  • Telemetry Service (In-Memory)                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### File Structure
```
backend/
├── main.py                    # FastAPI application
├── models/                    # Data models
│   ├── satellite.py
│   └── debris.py
├── services/                  # Business logic
│   ├── telemetry_service.py   # In-memory storage
│   ├── propagation_engine.py  # RK4 orbit propagation
│   ├── collision_detector.py  # KDTree collision detection
│   └── maneuver_planner.py    # Maneuver optimization
├── api/                       # API endpoints
│   ├── telemetry_api.py
│   ├── maneuver_api.py
│   ├── simulation_api.py
│   └── maneuver_schedule_api.py
└── utils/                     # Utilities
    ├── constants.py
    ├── orbital_math.py
    └── fuel_model.py

frontend/
├── src/
│   ├── App.jsx               # Main application
│   ├── components/
│   │   ├── SatelliteViewer.jsx    # 3D visualization
│   │   ├── OrbitLines.jsx         # Orbit trajectories
│   │   ├── CollisionAlerts.jsx    # Alert panel
│   │   ├── FuelPanel.jsx          # Fuel monitoring
│   │   ├── ManeuverTimeline.jsx   # Maneuver scheduling
│   │   └── SystemStatus.jsx       # Status display
│   └── api/
│       └── acmApi.js         # API client
└── package.json
```
