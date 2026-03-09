"""Collision detection using spatial indexing"""
from typing import List, Dict, Tuple
import numpy as np
from scipy.spatial import KDTree
from utils.constants import COLLISION_THRESHOLD, PREDICTION_HORIZON
from services.propagation_engine import propagation_engine
from services.telemetry_service import telemetry_service

class CollisionDetector:
    def __init__(self, threshold: float = COLLISION_THRESHOLD):
        self.threshold = threshold
    
    def detect_collisions(self, hours_ahead: float = PREDICTION_HORIZON) -> List[Dict]:
        """
        Detect potential collisions within prediction horizon
        Returns list of collision events
        """
        collisions = []
        satellites = telemetry_service.get_all_satellites()
        debris_objects = telemetry_service.get_all_debris()
        
        if not satellites:
            return collisions
        
        # Propagate all objects
        sat_trajectories = {}
        for sat in satellites:
            positions, _ = propagation_engine.propagate(
                sat.position, sat.velocity, hours_ahead
            )
            sat_trajectories[sat.object_id] = positions
        
        debris_trajectories = {}
        for deb in debris_objects:
            positions, _ = propagation_engine.propagate(
                deb.position, deb.velocity, hours_ahead
            )
            debris_trajectories[deb.object_id] = positions
        
        # Check for close approaches at each time step
        num_steps = len(next(iter(sat_trajectories.values())))
        
        for step in range(num_steps):
            # Build KDTree for debris at this time step
            if debris_trajectories:
                debris_positions = np.array([
                    debris_trajectories[deb_id][step] 
                    for deb_id in debris_trajectories
                ])
                tree = KDTree(debris_positions)
                debris_ids = list(debris_trajectories.keys())
                
                # Query for each satellite
                for sat_id, sat_traj in sat_trajectories.items():
                    sat_pos = sat_traj[step]
                    indices = tree.query_ball_point(sat_pos, self.threshold)
                    
                    for idx in indices:
                        time_to_collision = step * (hours_ahead * 3600 / num_steps) / 3600
                        collisions.append({
                            "satellite_id": sat_id,
                            "debris_id": debris_ids[idx],
                            "time_to_collision_hours": round(time_to_collision, 2),
                            "distance_km": round(
                                np.linalg.norm(sat_pos - debris_positions[idx]), 3
                            ),
                            "severity": "critical" if time_to_collision < 1 else "warning"
                        })
        
        return collisions

# Global instance
collision_detector = CollisionDetector()
