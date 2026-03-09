"""Orbital propagation engine using RK4 integration"""
from typing import List, Tuple
import numpy as np
from utils.orbital_math import propagate_orbit
from utils.constants import TIME_STEP, PREDICTION_HORIZON

class PropagationEngine:
    def __init__(self, time_step: float = TIME_STEP):
        self.time_step = time_step
    
    def propagate(self, position: List[float], velocity: List[float], 
                 hours: float = PREDICTION_HORIZON) -> Tuple[np.ndarray, np.ndarray]:
        """
        Propagate orbit forward in time
        Returns: (positions, velocities) for each time step
        """
        duration = hours * 3600  # Convert to seconds
        return propagate_orbit(position, velocity, duration, self.time_step)
    
    def predict_position_at_time(self, position: List[float], velocity: List[float], 
                                hours: float) -> Tuple[List[float], List[float]]:
        """
        Predict position and velocity at specific time
        Returns: (position, velocity) at target time
        """
        positions, velocities = self.propagate(position, velocity, hours)
        return positions[-1].tolist(), velocities[-1].tolist()

# Global instance
propagation_engine = PropagationEngine()
