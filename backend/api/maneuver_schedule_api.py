"""Maneuver scheduling API with optimization"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.maneuver_planner import maneuver_planner
from services.telemetry_service import telemetry_service
from services.collision_detector import collision_detector

router = APIRouter()

class ManeuverScheduleRequest(BaseModel):
    satellite_id: str
    maneuver_time: float  # Hours from now
    delta_v_vector: List[float]
    
    class Config:
        json_schema_extra = {
            "example": {
                "satellite_id": "SAT-001",
                "maneuver_time": 2.5,
                "delta_v_vector": [0.0, 0.005, 0.001]
            }
        }

@router.post("/maneuver/schedule")
async def schedule_maneuver(request: ManeuverScheduleRequest):
    """
    Schedule a maneuver for a satellite
    
    Constraints:
    - Minimum fuel usage optimization
    - Maintain orbital slot within 10 km
    - Thruster cooldown between burns (3600s)
    
    Fuel Model:
    - Uses Tsiolkovsky rocket equation
    - Tracks fuel consumption percentage
    """
    # Validate satellite exists
    satellite = telemetry_service.get_satellite(request.satellite_id)
    if not satellite:
        raise HTTPException(
            status_code=404, 
            detail=f"Satellite {request.satellite_id} not found"
        )
    
    # Compute delta-v magnitude
    import numpy as np
    delta_v_magnitude = np.linalg.norm(request.delta_v_vector)
    
    # Check fuel availability
    from utils.fuel_model import fuel_model
    fuel_cost = fuel_model.compute_fuel_percentage(delta_v_magnitude)
    
    if fuel_cost > satellite.fuel_remaining:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient fuel. Required: {fuel_cost:.2f}%, Available: {satellite.fuel_remaining:.2f}%"
        )
    
    # Create maneuver
    maneuver = {
        "satellite_id": request.satellite_id,
        "maneuver_type": "manual",
        "delta_v": request.delta_v_vector,
        "delta_v_magnitude": delta_v_magnitude,
        "fuel_cost_percent": fuel_cost,
        "execution_time_hours": request.maneuver_time,
        "execution_time_seconds": request.maneuver_time * 3600,
        "reason": "Manual maneuver request"
    }
    
    # Schedule with cooldown validation
    result = maneuver_planner.schedule_maneuver(request.satellite_id, maneuver)
    
    if result["status"] == "rejected":
        raise HTTPException(status_code=400, detail=result["reason"])
    
    # Update satellite fuel
    satellite.fuel_remaining -= fuel_cost
    telemetry_service.update_satellite(satellite)
    
    return {
        "status": "success",
        "message": f"Maneuver scheduled for {request.satellite_id}",
        "maneuver": result["maneuver"],
        "fuel_remaining": satellite.fuel_remaining,
        "total_scheduled_maneuvers": result["total_scheduled"]
    }

@router.get("/maneuver/schedule/{satellite_id}")
async def get_scheduled_maneuvers(satellite_id: str):
    """Get all scheduled maneuvers for a satellite"""
    satellite = telemetry_service.get_satellite(satellite_id)
    if not satellite:
        raise HTTPException(status_code=404, detail=f"Satellite {satellite_id} not found")
    
    maneuvers = maneuver_planner.get_scheduled_maneuvers(satellite_id)
    
    return {
        "satellite_id": satellite_id,
        "scheduled_maneuvers": maneuvers,
        "count": len(maneuvers),
        "fuel_remaining": satellite.fuel_remaining
    }

@router.post("/maneuver/optimize/{satellite_id}")
async def optimize_maneuvers(satellite_id: str):
    """
    Automatically optimize and schedule maneuvers for collision avoidance
    """
    satellite = telemetry_service.get_satellite(satellite_id)
    if not satellite:
        raise HTTPException(status_code=404, detail=f"Satellite {satellite_id} not found")
    
    # Detect collisions
    collisions = collision_detector.detect_collisions()
    sat_collisions = [c for c in collisions if c["satellite_id"] == satellite_id]
    
    if not sat_collisions:
        return {
            "satellite_id": satellite_id,
            "message": "No collision threats detected",
            "optimized_maneuvers": []
        }
    
    # Optimize maneuvers for each collision
    optimized_maneuvers = []
    total_fuel_cost = 0.0
    
    for collision in sat_collisions:
        maneuver = maneuver_planner.optimize_avoidance_maneuver(
            satellite_id,
            satellite.position,
            satellite.velocity,
            collision,
            satellite.fuel_remaining - total_fuel_cost
        )
        
        if maneuver:
            # Schedule the maneuver
            result = maneuver_planner.schedule_maneuver(satellite_id, maneuver)
            if result["status"] == "scheduled":
                optimized_maneuvers.append(maneuver)
                total_fuel_cost += maneuver["fuel_cost_percent"]
    
    # Update satellite fuel
    satellite.fuel_remaining -= total_fuel_cost
    telemetry_service.update_satellite(satellite)
    
    return {
        "satellite_id": satellite_id,
        "collision_threats": len(sat_collisions),
        "optimized_maneuvers": optimized_maneuvers,
        "total_fuel_cost": round(total_fuel_cost, 3),
        "fuel_remaining": satellite.fuel_remaining
    }
