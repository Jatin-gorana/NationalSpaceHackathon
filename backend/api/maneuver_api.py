"""Maneuver planning API endpoints"""
from fastapi import APIRouter, HTTPException
from services.collision_detector import collision_detector
from services.maneuver_planner import maneuver_planner
from services.telemetry_service import telemetry_service

router = APIRouter()

@router.get("/collisions")
async def detect_collisions(hours_ahead: float = 24):
    """
    Detect potential collisions within specified time horizon
    """
    if hours_ahead <= 0 or hours_ahead > 72:
        raise HTTPException(status_code=400, detail="hours_ahead must be between 0 and 72")
    
    collisions = collision_detector.detect_collisions(hours_ahead)
    
    return {
        "prediction_horizon_hours": hours_ahead,
        "collision_count": len(collisions),
        "collisions": collisions
    }

@router.post("/maneuvers/plan/{satellite_id}")
async def plan_maneuver(satellite_id: str):
    """
    Plan avoidance maneuvers for a specific satellite
    """
    satellite = telemetry_service.get_satellite(satellite_id)
    if not satellite:
        raise HTTPException(status_code=404, detail=f"Satellite {satellite_id} not found")
    
    # Check for collisions
    collisions = collision_detector.detect_collisions()
    sat_collisions = [c for c in collisions if c["satellite_id"] == satellite_id]
    
    maneuvers = []
    
    # Plan avoidance maneuvers
    for collision in sat_collisions:
        maneuver = maneuver_planner.plan_avoidance_maneuver(satellite_id, collision)
        if maneuver:
            maneuvers.append(maneuver)
    
    # Check station-keeping needs
    station_keeping = maneuver_planner.plan_station_keeping(
        satellite_id, satellite.position, satellite.assigned_slot
    )
    if station_keeping:
        maneuvers.append(station_keeping)
    
    return {
        "satellite_id": satellite_id,
        "maneuver_count": len(maneuvers),
        "maneuvers": maneuvers
    }

@router.get("/maneuvers/all")
async def plan_all_maneuvers():
    """
    Plan maneuvers for all satellites
    """
    satellites = telemetry_service.get_all_satellites()
    all_maneuvers = {}
    
    for satellite in satellites:
        collisions = collision_detector.detect_collisions()
        sat_collisions = [c for c in collisions if c["satellite_id"] == satellite.object_id]
        
        maneuvers = []
        for collision in sat_collisions:
            maneuver = maneuver_planner.plan_avoidance_maneuver(satellite.object_id, collision)
            if maneuver:
                maneuvers.append(maneuver)
        
        if maneuvers:
            all_maneuvers[satellite.object_id] = maneuvers
    
    return {
        "satellites_with_maneuvers": len(all_maneuvers),
        "maneuvers": all_maneuvers
    }
