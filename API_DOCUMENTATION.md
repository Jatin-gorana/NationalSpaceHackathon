# ACM API Documentation

## Base URL
```
http://localhost:8000/api
```

## Endpoints

### 1. POST /api/simulate/step

Run complete orbital simulation with collision detection.

**Request Body:**
```json
{
  "simulation_time_step": 24.0
}
```

**Parameters:**
- `simulation_time_step` (float): Prediction horizon in hours (0-72)

**Response:**
```json
{
  "simulation_time_step_hours": 24.0,
  "timestamp": "2026-03-09T12:00:00.000000",
  "physics_model": {
    "coordinate_system": "ECI (Earth-Centered Inertial)",
    "integration_method": "Runge-Kutta 4",
    "timestep_seconds": 10,
    "gravitational_constant": "μ = 398600.4418 km³/s²"
  },
  "collision_detection": {
    "algorithm": "KDTree spatial indexing",
    "search_radius_km": 50.0,
    "collision_threshold_meters": 100.0,
    "total_collisions": 2,
    "critical_collisions": 1,
    "warning_collisions": 1
  },
  "predicted_collisions": [
    {
      "satellite_id": "SAT-001",
      "debris_id": "DEB-001",
      "tca_seconds": 3600.0,
      "tca_hours": 1.0,
      "min_distance_km": 0.085,
      "min_distance_meters": 85.0,
      "severity": "critical",
      "collision_risk": true
    }
  ],
  "satellite_states": [
    {
      "object_id": "SAT-001",
      "current_position": [7000.0, 0.0, 0.0],
      "current_velocity": [0.0, 7.5, 0.0],
      "predicted_position": [6950.2, 1250.8, 0.0],
      "predicted_velocity": [0.05, 7.48, 0.0],
      "prediction_time_hours": 24.0,
      "trajectory_points": 8640
    }
  ],
  "debris_states": [...],
  "system_summary": {
    "total_satellites": 2,
    "total_debris": 3,
    "satellites_at_risk": 1
  }
}
```

**Physics Details:**
- Uses ECI coordinates
- RK4 integration with 10-second timestep
- Computes TCA for all close approaches
- KDTree optimization (O(N log N))

---

### 2. POST /api/telemetry

Ingest satellite or debris telemetry data.

**Request Body:**
```json
{
  "object_id": "SAT-001",
  "type": "satellite",
  "position": [7000.0, 0.0, 0.0],
  "velocity": [0.0, 7.5, 0.0],
  "timestamp": "2026-03-09T12:00:00Z"
}
```

**Parameters:**
- `object_id` (string): Unique identifier
- `type` (string): "satellite" or "debris"
- `position` (array): [x, y, z] in km (ECI)
- `velocity` (array): [vx, vy, vz] in km/s (ECI)
- `timestamp` (datetime): ISO 8601 format

**Response:**
```json
{
  "status": "success",
  "message": "Telemetry updated for SAT-001",
  "system_status": {
    "total_satellites": 2,
    "total_debris": 3,
    "operational_satellites": 2,
    "critical_satellites": 0,
    "timestamp": "2026-03-09T12:00:00.000000"
  }
}
```

---

### 3. GET /api/collisions

Detect potential collisions.

**Query Parameters:**
- `hours_ahead` (float, default=24): Prediction horizon

**Example:**
```
GET /api/collisions?hours_ahead=24
```

**Response:**
```json
{
  "prediction_horizon_hours": 24,
  "collision_count": 2,
  "collisions": [
    {
      "satellite_id": "SAT-001",
      "debris_id": "DEB-001",
      "tca_seconds": 3600.0,
      "tca_hours": 1.0,
      "min_distance_km": 0.085,
      "min_distance_meters": 85.0,
      "severity": "critical",
      "collision_risk": true
    }
  ]
}
```

---

### 4. POST /api/maneuvers/plan/{satellite_id}

Plan avoidance maneuvers for a satellite.

**Path Parameters:**
- `satellite_id` (string): Satellite identifier

**Example:**
```
POST /api/maneuvers/plan/SAT-001
```

**Response:**
```json
{
  "satellite_id": "SAT-001",
  "maneuver_count": 2,
  "maneuvers": [
    {
      "satellite_id": "SAT-001",
      "maneuver_type": "collision_avoidance",
      "delta_v": [0, 0, 0.01],
      "delta_v_magnitude": 0.01,
      "fuel_cost_percent": 0.1,
      "execution_time": 0.5,
      "reason": "Avoid collision with DEB-001"
    }
  ]
}
```

---

### 5. POST /api/simulate/propagate

Propagate a single orbit trajectory.

**Request Body:**
```json
{
  "position": [7000.0, 0.0, 0.0],
  "velocity": [0.0, 7.5, 0.0],
  "hours": 24
}
```

**Response:**
```json
{
  "duration_hours": 24,
  "total_steps": 8640,
  "sampled_steps": 87,
  "trajectory": {
    "positions": [[7000.0, 0.0, 0.0], ...],
    "velocities": [[0.0, 7.5, 0.0], ...],
    "timestamps": [0, 100, 200, ...]
  }
}
```

---

### 6. GET /api/telemetry/status

Get system status.

**Response:**
```json
{
  "total_satellites": 2,
  "total_debris": 3,
  "operational_satellites": 2,
  "critical_satellites": 0,
  "timestamp": "2026-03-09T12:00:00.000000"
}
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message"
}
```

**Status Codes:**
- 200: Success
- 400: Bad Request (invalid parameters)
- 404: Not Found (satellite/debris not found)
- 500: Internal Server Error

---

## Usage Examples

### Complete Workflow

```bash
# 1. Add satellites
curl -X POST http://localhost:8000/api/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "object_id": "SAT-001",
    "type": "satellite",
    "position": [7000.0, 0.0, 0.0],
    "velocity": [0.0, 7.5, 0.0],
    "timestamp": "2026-03-09T12:00:00Z"
  }'

# 2. Add debris
curl -X POST http://localhost:8000/api/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "object_id": "DEB-001",
    "type": "debris",
    "position": [7000.0, 50.0, 10.0],
    "velocity": [0.05, 7.48, 0.01],
    "timestamp": "2026-03-09T12:00:00Z"
  }'

# 3. Run simulation
curl -X POST http://localhost:8000/api/simulate/step \
  -H "Content-Type: application/json" \
  -d '{"simulation_time_step": 24.0}'

# 4. Plan maneuvers
curl -X POST http://localhost:8000/api/maneuvers/plan/SAT-001
```

---

## Performance Notes

- Simulation step with 50 satellites + 1000 debris: ~2-5 seconds
- KDTree optimization reduces collision checks by 99%
- 10-second timestep provides < 1m position accuracy
- Trajectory caching available for repeated queries
