"""Simulation and propagation API endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from services.propagation_engine import propagation_engine
from services.collision_detector import collision_detector
from services.telemetry_service import telemetry_service

router = APIRouter()

class PropagationRequest(BaseModel):
    position: List[float]
    velocity: List[float]
    hours: float = 24
    
    class Config:
        json_schema_extra = {
            "example": {
                "position": [7000.0, 0.0, 0.0],
                "velocity": [0.0, 7.5, 0.0],
                "hours": 24
            }
        }

class SimulationStepRequest(BaseModel):
    simulation_time_step: float = 24.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "simulation_time_step": 24.0
            }
        }

@router.post("/simulate/propagate")
async def propagate(request: PropagationRequest):
    """
    Propagate orbit forward in time using RK4 integration in ECI coordinates
    """
    if request.hours <= 0 or request.hours > 168:
        raise HTTPException(status_code=400, detail="hours must be between 0 and 168")
    
    positions, velocities, timestamps = propagation_engine.propagate(
        request.position, request.velocity, request.hours
    )
    
    # Return sampled trajectory (every 10th point to reduce payload)
    sample_rate = max(1, len(positions) // 100)
    
    return {
        "duration_hours": request.hours,
        "total_steps": len(positions),
        "sampled_steps": len(positions[::sample_rate]),
        "trajectory": {
            "positions": positions[::sample_rate].tolist(),
            "velocities": velocities[::sample_rate].tolist(),
            "timestamps": timestamps[::sample_rate].tolist()
        }
    }

@router.post("/simulate/predict")
async def predict_position(request: PropagationRequest):
    """
    Predict position at specific time using RK4 propagation
    """
    position, velocity = propagation_engine.predict_position_at_time(
        request.position, request.velocity, request.hours
    )
    
    return {
        "time_hours": request.hours,
        "predicted_position": position,
        "predicted_velocity": velocity
    }

@router.post("/simulate/step")
async def simulation_step(request: SimulationStepRequest):
    """
    Run complete simulation step with orbital propagation and collision detection
    
    Physics:
    - Uses Earth-Centered Inertial (ECI) coordinates
    - RK4 integration with 10-second timestep
    - Gravitational force: d²r/dt² = -μr / |r|³
    
    Optimization:
    - KDTree spatial indexing (O(N log N) vs O(N²))
    - 50 km search radius for close approaches
    - TCA computation for collision pairs
    
    Returns:
    - Predicted collisions with TCA and minimum distance
    - Updated satellite states
    - Updated debris states
    """
    if request.simulation_time_step <= 0 or request.simulation_time_step > 72:
        raise HTTPException(
            status_code=400, 
            detail="simulation_time_step must be between 0 and 72 hours"
        )
    
    # Get current system state
    satellites = telemetry_service.get_all_satellites()
    debris_objects = telemetry_service.get_all_debris()
    
    if not satellites:
        raise HTTPException(status_code=400, detail="No satellites in system")
    
    # Propagate all satellites
    satellite_states = []
    for sat in satellites:
        positions, velocities, timestamps = propagation_engine.propagate(
            sat.position, sat.velocity, request.simulation_time_step
        )
        
        # Get final state
        final_pos = positions[-1].tolist()
        final_vel = velocities[-1].tolist()
        
        satellite_states.append({
            "object_id": sat.object_id,
            "current_position": sat.position,
            "current_velocity": sat.velocity,
            "predicted_position": final_pos,
            "predicted_velocity": final_vel,
            "prediction_time_hours": request.simulation_time_step,
            "trajectory_points": len(positions)
        })
    
    # Propagate all debris
    debris_states = []
    for deb in debris_objects:
        positions, velocities, timestamps = propagation_engine.propagate(
            deb.position, deb.velocity, request.simulation_time_step
        )
        
        final_pos = positions[-1].tolist()
        final_vel = velocities[-1].tolist()
        
        debris_states.append({
            "object_id": deb.object_id,
            "current_position": deb.position,
            "current_velocity": deb.velocity,
            "predicted_position": final_pos,
            "predicted_velocity": final_vel,
            "size_estimate": deb.size_estimate
        })
    
    # Detect collisions using optimized KDTree algorithm
    predicted_collisions = collision_detector.detect_collisions(request.simulation_time_step)
    
    # Compute statistics
    critical_collisions = [c for c in predicted_collisions if c["severity"] == "critical"]
    warning_collisions = [c for c in predicted_collisions if c["severity"] == "warning"]
    
    return {
        "simulation_time_step_hours": request.simulation_time_step,
        "timestamp": telemetry_service.get_system_status()["timestamp"],
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
            "total_collisions": len(predicted_collisions),
            "critical_collisions": len(critical_collisions),
            "warning_collisions": len(warning_collisions)
        },
        "predicted_collisions": predicted_collisions,
        "satellite_states": satellite_states,
        "debris_states": debris_states,
        "system_summary": {
            "total_satellites": len(satellite_states),
            "total_debris": len(debris_states),
            "satellites_at_risk": len(set(c["satellite_id"] for c in predicted_collisions))
        }
    }
