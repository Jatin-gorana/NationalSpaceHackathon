"""Collision detection using spatial indexing and TCA computation"""
from typing import List, Dict, Tuple
import numpy as np
from scipy.spatial import KDTree
from utils.constants import COLLISION_THRESHOLD, PREDICTION_HORIZON, SPATIAL_SEARCH_RADIUS
from utils.orbital_math import compute_tca_and_distance
from services.propagation_engine import propagation_engine
from services.telemetry_service import telemetry_service

class CollisionDetector:
    def __init__(self, threshold: float = COLLISION_THRESHOLD, 
                 search_radius: float = SPATIAL_SEARCH_RADIUS):
        self.threshold = threshold
        self.search_radius = search_radius
    
    def detect_collisions(self, hours_ahead: float = PREDICTION_HORIZON) -> List[Dict]:
        """
        Detect potential collisions using optimized KDTree spatial indexing
        
        Algorithm:
        1. Propagate all objects using RK4
        2. Build KDTree for debris positions at each timestep
        3. Query satellites within search_radius (50 km)
        4. Compute TCA and minimum distance for close approaches
        5. Flag collisions if distance < 100 meters
        
        Returns list of collision events with TCA
        """
        collisions = []
        satellites = telemetry_service.get_all_satellites()
        debris_objects = telemetry_service.get_all_debris()
        
        if not satellites or not debris_objects:
            return collisions
        
        # Propagate all objects
        sat_trajectories = {}
        for sat in satellites:
            positions, velocities, timestamps = propagation_engine.propagate(
                sat.position, sat.velocity, hours_ahead
            )
            sat_trajectories[sat.object_id] = (positions, velocities, timestamps)
        
        debris_trajectories = {}
        for deb in debris_objects:
            positions, velocities, timestamps = propagation_engine.propagate(
                deb.position, deb.velocity, hours_ahead
            )
            debris_trajectories[deb.object_id] = (positions, velocities, timestamps)
        
        # Get number of timesteps
        num_steps = len(sat_trajectories[next(iter(sat_trajectories))][0])
        
        # Check for close approaches using KDTree at each timestep
        close_pairs = set()
        
        for step in range(num_steps):
            # Build KDTree for debris at this timestep
            debris_positions = np.array([
                debris_trajectories[deb_id][0][step] 
                for deb_id in debris_trajectories
            ])
            tree = KDTree(debris_positions)
            debris_ids = list(debris_trajectories.keys())
            
            # Query for each satellite within search radius
            for sat_id, (sat_pos, _, _) in sat_trajectories.items():
                indices = tree.query_ball_point(sat_pos[step], self.search_radius)
                
                for idx in indices:
                    close_pairs.add((sat_id, debris_ids[idx]))
        
        # Compute TCA and minimum distance for close pairs
        for sat_id, deb_id in close_pairs:
            sat_pos, _, timestamps = sat_trajectories[sat_id]
            deb_pos, _, _ = debris_trajectories[deb_id]
            
            tca_time, min_distance, tca_idx = compute_tca_and_distance(
                sat_pos, deb_pos, timestamps
            )
            
            # Flag as collision if distance < threshold
            if min_distance < self.threshold:
                collisions.append({
                    "satellite_id": sat_id,
                    "debris_id": deb_id,
                    "tca_seconds": round(tca_time, 2),
                    "tca_hours": round(tca_time / 3600, 3),
                    "min_distance_km": round(min_distance, 6),
                    "min_distance_meters": round(min_distance * 1000, 2),
                    "severity": "critical" if tca_time < 3600 else "warning",
                    "collision_risk": True
                })
        
        # Sort by TCA
        collisions.sort(key=lambda x: x["tca_seconds"])
        
        return collisions

# Global instance
collision_detector = CollisionDetector()
