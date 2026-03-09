"""Maneuver planning for collision avoidance"""
from typing import List, Dict, Optional
import numpy as np
from utils.orbital_math import distance
from utils.constants import SLOT_TOLERANCE

class ManeuverPlanner:
    def __init__(self):
        self.min_delta_v = 0.001  # Minimum delta-v in km/s
    
    def plan_avoidance_maneuver(self, satellite_id: str, 
                               collision_info: Dict) -> Optional[Dict]:
        """
        Plan collision avoidance maneuver
        Returns maneuver plan with delta-v
        """
        # Simple radial boost strategy
        delta_v_magnitude = 0.01  # 10 m/s radial boost
        
        maneuver = {
            "satellite_id": satellite_id,
            "maneuver_type": "collision_avoidance",
            "delta_v": [0, 0, delta_v_magnitude],  # Radial boost
            "delta_v_magnitude": delta_v_magnitude,
            "fuel_cost_percent": self._estimate_fuel_cost(delta_v_magnitude),
            "execution_time": collision_info.get("time_to_collision_hours", 0) - 0.5,
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
            # Calculate required delta-v (simplified)
            direction = np.array(assigned_slot) - np.array(current_pos)
            direction = direction / np.linalg.norm(direction)
            delta_v_magnitude = min(0.005, deviation * 0.001)  # Scale with deviation
            delta_v = (direction * delta_v_magnitude).tolist()
            
            return {
                "satellite_id": satellite_id,
                "maneuver_type": "station_keeping",
                "delta_v": delta_v,
                "delta_v_magnitude": delta_v_magnitude,
                "fuel_cost_percent": self._estimate_fuel_cost(delta_v_magnitude),
                "deviation_km": round(deviation, 2),
                "reason": "Maintain assigned orbital slot"
            }
        
        return None
    
    def _estimate_fuel_cost(self, delta_v: float) -> float:
        """Estimate fuel cost as percentage (simplified)"""
        # Rough estimate: 1 m/s costs ~0.1% fuel
        return round(delta_v * 10, 2)

# Global instance
maneuver_planner = ManeuverPlanner()
