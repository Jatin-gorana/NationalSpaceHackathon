"""Advanced maneuver planning with optimization"""
from typing import List, Dict, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
from utils.orbital_math import distance
from utils.constants import (
    SLOT_TOLERANCE, LOW_FUEL_THRESHOLD, GRAVEYARD_ALTITUDE, 
    EARTH_RADIUS, THRUSTER_COOLDOWN, COMMUNICATION_DELAY
)
from utils.fuel_model import fuel_model

class ManeuverPlanner:
    def __init__(self, thruster_cooldown: float = THRUSTER_COOLDOWN):
        """
        Initialize maneuver planner
        
        Args:
            thruster_cooldown: Minimum time between burns in seconds
        """
        self.min_delta_v = 0.001  # Minimum delta-v in km/s
        self.max_delta_v = 0.1  # Maximum delta-v per burn in km/s
        self.thruster_cooldown = thruster_cooldown
        self.scheduled_maneuvers: Dict[str, List[Dict]] = {}
        self.communication_delay = COMMUNICATION_DELAY
    
    def optimize_avoidance_maneuver(self, satellite_id: str, 
                                   satellite_pos: List[float],
                                   satellite_vel: List[float],
                                   collision_info: Dict,
                                   fuel_remaining: float = 100.0) -> Optional[Dict]:
        """
        Optimize collision avoidance maneuver with fuel minimization
        
        Strategy:
        1. Compute optimal delta-v direction (perpendicular to velocity)
        2. Minimize delta-v magnitude while ensuring safe separation
        3. Check fuel budget and orbital slot constraints
        """
        tca_hours = collision_info.get("tca_hours", 1.0)
        min_distance = collision_info.get("min_distance_km", 0.1)
        
        # Compute optimal maneuver direction (perpendicular to velocity)
        vel = np.array(satellite_vel)
        pos = np.array(satellite_pos)
        
        # Radial direction
        radial = pos / np.linalg.norm(pos)
        
        # Cross-track direction (perpendicular to velocity and radial)
        cross_track = np.cross(vel, radial)
        cross_track = cross_track / np.linalg.norm(cross_track)
        
        # Optimize delta-v magnitude (minimum to achieve 1 km separation)
        target_separation = 1.0  # km
        required_delta_v = max(0.005, (target_separation - min_distance) * 0.01)
        required_delta_v = min(required_delta_v, self.max_delta_v)
        
        # Check fuel budget
        fuel_cost = fuel_model.compute_fuel_percentage(required_delta_v)
        if fuel_cost > fuel_remaining:
            return None
        
        # Compute execution time (execute at TCA - 30 minutes)
        execution_time = max(0.5, tca_hours - 0.5)
        
        delta_v_vector = (cross_track * required_delta_v).tolist()
        
        maneuver = {
            "satellite_id": satellite_id,
            "maneuver_type": "collision_avoidance",
            "delta_v": delta_v_vector,
            "delta_v_magnitude": required_delta_v,
            "fuel_cost_percent": round(fuel_cost, 3),
            "execution_time_hours": round(execution_time, 2),
            "execution_time_seconds": round(execution_time * 3600, 0),
            "target_separation_km": target_separation,
            "collision_object": collision_info.get("debris_id", "unknown"),
            "reason": f"Avoid collision with {collision_info.get('debris_id', 'unknown')}",
            "optimized": True
        }
        
        return maneuver
    
    def plan_avoidance_maneuver(self, satellite_id: str, 
                               collision_info: Dict) -> Optional[Dict]:
        """Legacy method for backward compatibility"""
        delta_v_magnitude = 0.01
        
        maneuver = {
            "satellite_id": satellite_id,
            "maneuver_type": "collision_avoidance",
            "delta_v": [0, 0, delta_v_magnitude],
            "delta_v_magnitude": delta_v_magnitude,
            "fuel_cost_percent": fuel_model.compute_fuel_percentage(delta_v_magnitude),
            "execution_time": collision_info.get("tca_hours", 1.0) - 0.5,
            "reason": f"Avoid collision with {collision_info.get('debris_id', 'unknown')}"
        }
        
        return maneuver
    
    def plan_station_keeping(self, satellite_id: str, 
                            current_pos: List[float], 
                            assigned_slot: List[float]) -> Optional[Dict]:
        """
        Plan station-keeping maneuver to maintain orbital slot
        """
        deviation = distance(current_pos, assigned_slot)
        
        if deviation > SLOT_TOLERANCE:
            direction = np.array(assigned_slot) - np.array(current_pos)
            direction = direction / np.linalg.norm(direction)
            delta_v_magnitude = min(0.005, deviation * 0.001)
            delta_v = (direction * delta_v_magnitude).tolist()
            
            return {
                "satellite_id": satellite_id,
                "maneuver_type": "station_keeping",
                "delta_v": delta_v,
                "delta_v_magnitude": delta_v_magnitude,
                "fuel_cost_percent": fuel_model.compute_fuel_percentage(delta_v_magnitude),
                "deviation_km": round(deviation, 2),
                "reason": "Maintain assigned orbital slot"
            }
        
        return None
    
    def schedule_maneuver(self, satellite_id: str, maneuver: Dict) -> Dict:
        """
        Schedule a maneuver with cooldown validation
        """
        if satellite_id not in self.scheduled_maneuvers:
            self.scheduled_maneuvers[satellite_id] = []
        
        # Check cooldown constraint
        if self.scheduled_maneuvers[satellite_id]:
            last_maneuver = self.scheduled_maneuvers[satellite_id][-1]
            time_since_last = maneuver.get("execution_time_seconds", 0) - \
                            last_maneuver.get("execution_time_seconds", 0)
            
            if time_since_last < self.thruster_cooldown:
                return {
                    "status": "rejected",
                    "reason": f"Thruster cooldown required: {self.thruster_cooldown}s",
                    "time_until_ready": self.thruster_cooldown - time_since_last
                }
        
        # Add to schedule
        maneuver["scheduled_at"] = datetime.utcnow().isoformat()
        maneuver["status"] = "scheduled"
        self.scheduled_maneuvers[satellite_id].append(maneuver)
        
        return {
            "status": "scheduled",
            "maneuver": maneuver,
            "total_scheduled": len(self.scheduled_maneuvers[satellite_id])
        }
    
    def get_scheduled_maneuvers(self, satellite_id: str) -> List[Dict]:
        """Get all scheduled maneuvers for a satellite"""
        return self.scheduled_maneuvers.get(satellite_id, [])
    
    def clear_executed_maneuvers(self, satellite_id: str, current_time: float):
        """Remove executed maneuvers from schedule"""
        if satellite_id in self.scheduled_maneuvers:
            self.scheduled_maneuvers[satellite_id] = [
                m for m in self.scheduled_maneuvers[satellite_id]
                if m.get("execution_time_seconds", 0) > current_time
            ]
    
    def plan_orbit_recovery(self, satellite_id: str,
                           current_pos: List[float],
                           current_vel: List[float],
                           assigned_slot: List[float],
                           fuel_remaining: float,
                           execution_delay: float = 60.0) -> Optional[Dict]:
        """
        Plan orbit recovery maneuver to return to assigned slot
        
        Args:
            satellite_id: Satellite identifier
            current_pos: Current position [x, y, z]
            current_vel: Current velocity [vx, vy, vz]
            assigned_slot: Target position [x, y, z]
            fuel_remaining: Remaining fuel percentage
            execution_delay: Delay before execution (seconds)
        
        Returns:
            Recovery maneuver dict or None if not needed
        """
        deviation = distance(current_pos, assigned_slot)
        
        # Only recover if deviation > tolerance
        if deviation <= SLOT_TOLERANCE:
            return None
        
        # Compute direction to assigned slot
        direction = np.array(assigned_slot) - np.array(current_pos)
        direction_norm = np.linalg.norm(direction)
        
        if direction_norm < 0.001:
            return None
        
        direction = direction / direction_norm
        
        # Compute required delta-v (proportional to deviation)
        # Use gentle correction: 0.1% of deviation per maneuver
        delta_v_magnitude = min(0.01, deviation * 0.001)
        delta_v_magnitude = max(self.min_delta_v, delta_v_magnitude)
        
        # Check fuel budget
        fuel_cost = fuel_model.compute_fuel_percentage(delta_v_magnitude)
        if fuel_cost > fuel_remaining:
            return None
        
        delta_v_vector = (direction * delta_v_magnitude).tolist()
        
        return {
            "satellite_id": satellite_id,
            "maneuver_type": "orbit_recovery",
            "delta_v": delta_v_vector,
            "delta_v_magnitude": delta_v_magnitude,
            "fuel_cost_percent": round(fuel_cost, 3),
            "execution_time_seconds": execution_delay,
            "execution_time_hours": round(execution_delay / 3600, 2),
            "deviation_km": round(deviation, 2),
            "target_slot": assigned_slot,
            "reason": f"Return to assigned slot (deviation: {deviation:.2f} km)",
            "priority": "medium"
        }
    
    def plan_graveyard_orbit(self, satellite_id: str,
                            current_pos: List[float],
                            current_vel: List[float],
                            fuel_remaining: float) -> Optional[Dict]:
        """
        Plan graveyard orbit maneuver for low-fuel satellites
        
        Strategy: Raise orbit to graveyard altitude (2500 km above current)
        
        Args:
            satellite_id: Satellite identifier
            current_pos: Current position [x, y, z]
            current_vel: Current velocity [vx, vy, vz]
            fuel_remaining: Remaining fuel percentage
        
        Returns:
            Graveyard maneuver dict or None if insufficient fuel
        """
        # Compute current altitude
        current_radius = np.linalg.norm(current_pos)
        current_altitude = current_radius - EARTH_RADIUS
        
        # Target graveyard altitude
        target_altitude = current_altitude + GRAVEYARD_ALTITUDE
        target_radius = EARTH_RADIUS + target_altitude
        
        # Compute Hohmann transfer delta-v
        # For circular orbit raise: Δv = √(μ/r₁) * (√(2r₂/(r₁+r₂)) - 1)
        mu = 398600.4418  # Earth's gravitational parameter
        
        # First burn (raise apogee)
        dv1 = np.sqrt(mu / current_radius) * (np.sqrt(2 * target_radius / (current_radius + target_radius)) - 1)
        
        # Second burn (circularize at apogee) - we'll skip this to save fuel
        # Just do the first burn to raise apogee
        
        delta_v_magnitude = abs(dv1)
        
        # Check fuel budget
        fuel_cost = fuel_model.compute_fuel_percentage(delta_v_magnitude)
        if fuel_cost > fuel_remaining:
            # Use all remaining fuel
            delta_v_magnitude = fuel_remaining * 0.01  # Rough approximation
        
        # Apply delta-v in velocity direction
        vel = np.array(current_vel)
        vel_norm = np.linalg.norm(vel)
        if vel_norm < 0.001:
            return None
        
        vel_direction = vel / vel_norm
        delta_v_vector = (vel_direction * delta_v_magnitude).tolist()
        
        return {
            "satellite_id": satellite_id,
            "maneuver_type": "graveyard_orbit",
            "delta_v": delta_v_vector,
            "delta_v_magnitude": delta_v_magnitude,
            "fuel_cost_percent": round(fuel_cost, 3),
            "execution_time_seconds": 30.0,  # Execute immediately
            "execution_time_hours": round(30.0 / 3600, 3),
            "current_altitude_km": round(current_altitude, 2),
            "target_altitude_km": round(target_altitude, 2),
            "reason": f"Low fuel ({fuel_remaining:.1f}%) - moving to graveyard orbit",
            "priority": "critical"
        }
    
    def check_communication_window(self, satellite_pos: List[float],
                                   ground_station_pos: List[float] = None) -> bool:
        """
        Check if satellite is in communication window with ground station
        
        Simplified: Check if satellite is above horizon (line of sight)
        
        Args:
            satellite_pos: Satellite position [x, y, z]
            ground_station_pos: Ground station position (default: [EARTH_RADIUS, 0, 0])
        
        Returns:
            True if in communication window
        """
        if ground_station_pos is None:
            # Default ground station at equator
            ground_station_pos = [EARTH_RADIUS, 0, 0]
        
        sat_pos = np.array(satellite_pos)
        gs_pos = np.array(ground_station_pos)
        
        # Vector from ground station to satellite
        to_sat = sat_pos - gs_pos
        
        # Check if satellite is above horizon (dot product > 0)
        # Simplified: just check if satellite is on same hemisphere
        dot_product = np.dot(to_sat, gs_pos)
        
        return dot_product > 0

# Global instance
maneuver_planner = ManeuverPlanner()
