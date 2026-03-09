# Autonomous Constellation Manager (ACM)

Satellite collision avoidance and orbital management system for monitoring 50+ satellites and thousands of debris objects.

## Features

- Real-time telemetry ingestion for satellites and debris
- 24-hour collision prediction using RK4 orbital propagation
- Earth-Centered Inertial (ECI) coordinate system
- High-precision 10-second timestep integration
- Optimized collision detection with KDTree spatial indexing (O(N log N))
- Time of Closest Approach (TCA) computation
- 50 km search radius with 100m collision threshold
- Automated maneuver planning for collision avoidance
- Station-keeping to maintain satellites within 10km of assigned slots
- Fuel-optimized maneuver calculations

## Tech Stack

- Backend: Python + FastAPI
- Physics: NumPy + SciPy
- Spatial Indexing: KDTree
- Simulation: Runge-Kutta 4 orbital propagation
- Deployment: Docker

## Quick Start

### Local Development

```bash
cd acm-system/backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Docker Deployment

```bash
cd acm-system
docker-compose -f docker/docker-compose.yml up --build
```

API will be available at `http://localhost:8000`

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
│   └── simulation_api.py
└── utils/                     # Utilities
    ├── constants.py
    └── orbital_math.py
```
