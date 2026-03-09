"""AI-powered optimization API endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.ai_optimizer import ai_optimizer
from services.telemetry_service import telemetry_service
from services.collision_detector import collision_detector
from services.maneuver_planner import maneuver_planner

router = APIRouter()

class AIOptimizationRequest(BaseModel):
    satellite_id: str
    population_size: Optional[int] = 50
    generations: Optional[int] = 100
    
    class Config:
        json_schema_extra = {
            "example": {
                "satellite_id": "SAT-001",
                "population_size": 50,
                "generations": 100
            }
        }

@router.post("/ai/optimize/{satellite_id}")
async def ai_optimize_maneuvers(satellite_id: str, request: Optional[AIOptimizationRequest] = None):
    """
    Use AI (Genetic Algorithm) to optimize maneuvers for minimum fuel usage
    
    Algorithm:
    - Population-based search
    - Fitness: collision avoidance + fuel efficiency + slot maintenance
    - Evolution: selection, crossover, mutation
    - Converges to optimal maneuver plan
    """
    # Get satellite
    satellite = telemetry_service.get_satellite(satellite_id)
    if not satellite:
        raise HTTPException(status_code=404, detail=f"Satellite {satellite_id} not found")
    
    # Detect collision threats
    collisions = collision_detector.detect_collisions()
    sat_collisions = [c for c in collisions if c["satellite_id"] == satellite_id]
    
    if not sat_collisions:
        return {
            "satellite_id": satellite_id,
            "status": "no_threats",
            "message": "No collision threats detected",
            "ai_maneuvers": []
        }
    
    # Configure optimizer
    if request:
        optimizer = ai_optimizer
        optimizer.population_size = request.population_size or 50
        optimizer.generations = request.generations or 100
    else:
        optimizer = ai_optimizer
    
    # Run AI optimization
    ai_maneuvers = []
    total_fuel_cost = 0.0
    
    for collision in sat_collisions[:3]:  # Optimize for top 3 threats
        maneuver = optimizer.optimize(
            satellite.position,
            satellite.velocity,
            satellite.assigned_slot,
            [collision],
            satellite.fuel_remaining - total_fuel_cost
        )
        
        if maneuver:
            # Schedule the maneuver
            result = maneuver_planner.schedule_maneuver(satellite_id, maneuver)
            if result["status"] == "scheduled":
                ai_maneuvers.append(maneuver)
                total_fuel_cost += maneuver["fuel_cost_percent"]
    
    # Update satellite fuel
    if ai_maneuvers:
        satellite.fuel_remaining -= total_fuel_cost
        telemetry_service.update_satellite(satellite)
    
    return {
        "satellite_id": satellite_id,
        "status": "optimized",
        "collision_threats": len(sat_collisions),
        "ai_maneuvers": ai_maneuvers,
        "total_fuel_cost": round(total_fuel_cost, 3),
        "fuel_remaining": satellite.fuel_remaining,
        "optimization_method": "genetic_algorithm",
        "algorithm_params": {
            "population_size": optimizer.population_size,
            "generations": optimizer.generations,
            "mutation_rate": optimizer.mutation_rate,
            "crossover_rate": optimizer.crossover_rate
        }
    }

@router.post("/ai/optimize-fleet")
async def ai_optimize_fleet():
    """
    AI-optimize maneuvers for entire satellite fleet
    """
    satellites = telemetry_service.get_all_satellites()
    
    if not satellites:
        raise HTTPException(status_code=400, detail="No satellites in system")
    
    fleet_results = []
    
    for satellite in satellites:
        # Detect collisions for this satellite
        collisions = collision_detector.detect_collisions()
        sat_collisions = [c for c in collisions if c["satellite_id"] == satellite.object_id]
        
        if not sat_collisions:
            continue
        
        # Optimize
        ai_maneuvers = []
        total_fuel_cost = 0.0
        
        for collision in sat_collisions[:2]:  # Top 2 threats per satellite
            maneuver = ai_optimizer.optimize(
                satellite.position,
                satellite.velocity,
                satellite.assigned_slot,
                [collision],
                satellite.fuel_remaining - total_fuel_cost
            )
            
            if maneuver:
                result = maneuver_planner.schedule_maneuver(satellite.object_id, maneuver)
                if result["status"] == "scheduled":
                    ai_maneuvers.append(maneuver)
                    total_fuel_cost += maneuver["fuel_cost_percent"]
        
        if ai_maneuvers:
            satellite.fuel_remaining -= total_fuel_cost
            telemetry_service.update_satellite(satellite)
            
            fleet_results.append({
                "satellite_id": satellite.object_id,
                "maneuvers": ai_maneuvers,
                "fuel_cost": round(total_fuel_cost, 3),
                "fuel_remaining": satellite.fuel_remaining
            })
    
    return {
        "status": "fleet_optimized",
        "satellites_optimized": len(fleet_results),
        "total_satellites": len(satellites),
        "results": fleet_results,
        "optimization_method": "genetic_algorithm"
    }

@router.get("/ai/status")
async def get_ai_status():
    """Get AI optimizer configuration and status"""
    return {
        "optimizer": "genetic_algorithm",
        "status": "ready",
        "configuration": {
            "population_size": ai_optimizer.population_size,
            "generations": ai_optimizer.generations,
            "mutation_rate": ai_optimizer.mutation_rate,
            "crossover_rate": ai_optimizer.crossover_rate,
            "max_delta_v": ai_optimizer.max_delta_v
        },
        "capabilities": [
            "Multi-objective optimization",
            "Collision avoidance",
            "Fuel minimization",
            "Orbital slot maintenance",
            "Constraint handling"
        ]
    }

@router.post("/ai/auto-resolve")
async def auto_resolve_collisions():
    """
    Automatically resolve all collision risks using AI optimization
    Applies maneuvers to satellites at risk to avoid collisions
    """
    from services.simulation_engine import simulation_engine
    
    # Get satellites at risk
    satellites = telemetry_service.get_all_satellites()
    at_risk_satellites = [sat for sat in satellites if sat.object_id in simulation_engine.collision_risks]
    
    if not at_risk_satellites:
        return {
            "status": "no_risks",
            "message": "No collision risks detected",
            "satellites_resolved": 0
        }
    
    resolved = []
    
    for satellite in at_risk_satellites:
        # Calculate avoidance maneuver (simple: perpendicular to velocity)
        import numpy as np
        vel = np.array(satellite.velocity)
        vel_mag = np.linalg.norm(vel)
        
        # Create perpendicular delta-v (0.05 km/s = 50 m/s)
        perpendicular = np.array([-vel[1], vel[0], 0])
        if np.linalg.norm(perpendicular) > 0:
            perpendicular = perpendicular / np.linalg.norm(perpendicular)
        delta_v = perpendicular * 0.05  # 50 m/s maneuver
        
        # Apply maneuver
        success = simulation_engine.apply_maneuver(satellite.object_id, delta_v.tolist())
        
        if success:
            resolved.append({
                "satellite_id": satellite.object_id,
                "delta_v": delta_v.tolist(),
                "fuel_remaining": satellite.fuel_remaining
            })
    
    return {
        "status": "resolved",
        "message": f"Applied avoidance maneuvers to {len(resolved)} satellites",
        "satellites_resolved": len(resolved),
        "total_at_risk": len(at_risk_satellites),
        "maneuvers": resolved
    }
