"""Simulation and propagation API endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.propagation_engine import propagation_engine

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

@router.post("/simulate/propagate")
async def propagate(request: PropagationRequest):
    """
    Propagate orbit forward in time using RK4 integration
    """
    if request.hours <= 0 or request.hours > 168:
        raise HTTPException(status_code=400, detail="hours must be between 0 and 168")
    
    positions, velocities = propagation_engine.propagate(
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
            "velocities": velocities[::sample_rate].tolist()
        }
    }

@router.post("/simulate/predict")
async def predict_position(request: PropagationRequest):
    """
    Predict position at specific time
    """
    position, velocity = propagation_engine.predict_position_at_time(
        request.position, request.velocity, request.hours
    )
    
    return {
        "time_hours": request.hours,
        "predicted_position": position,
        "predicted_velocity": velocity
    }
