"""Orbital propagation engine using RK4 integration in ECI coordinates"""
from typing import List, Tuple, Dict
import numpy as np
from utils.orbital_math import propagate_orbit
from utils.constants import TIME_STEP, PREDICTION_HORIZON

class PropagationEngine:
    def __init__(self, time_step: float = TIME_STEP):
        self.time_step = time_step
        self.trajectory_cache: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    
    def propagate(self, position: List[float], velocity: List[float], 
                 hours: float = PREDICTION_HORIZON) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Propagate orbit forward in time using RK4 in ECI coordinates
        Returns: (positions, velocities, timestamps) for each time step
        """
        duration = hours * 3600  # Convert to seconds
        return propagate_orbit(position, velocity, duration, self.time_step)
    
    def propagate_with_cache(self, object_id: str, position: List[float], 
                            velocity: List[float], hours: float = PREDICTION_HORIZON) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Propagate orbit with caching for performance optimization
        """
        cache_key = f"{object_id}_{hours}"
        
        if cache_key not in self.trajectory_cache:
            self.trajectory_cache[cache_key] = self.propagate(position, velocity, hours)
        
        return self.trajectory_cache[cache_key]
    
    def clear_cache(self):
        """Clear trajectory cache"""
        self.trajectory_cache.clear()
    
    def predict_position_at_time(self, position: List[float], velocity: List[float], 
                                hours: float) -> Tuple[List[float], List[float]]:
        """
        Predict position and velocity at specific time
        Returns: (position, velocity) at target time
        """
        positions, velocities, _ = self.propagate(position, velocity, hours)
        return positions[-1].tolist(), velocities[-1].tolist()

# Global instance
propagation_engine = PropagationEngine()
