"""Orbital mechanics utility functions"""
import numpy as np
from typing import List, Tuple, Optional
from .constants import MU_EARTH

def distance(pos1: List[float], pos2: List[float]) -> float:
    """Calculate Euclidean distance between two positions"""
    return np.linalg.norm(np.array(pos1) - np.array(pos2))

def orbital_acceleration(position: np.ndarray) -> np.ndarray:
    """
    Calculate gravitational acceleration at given position (ECI coordinates)
    Using Newton's law: a = -μr / |r|³
    """
    r = np.linalg.norm(position)
    if r < 1e-6:  # Avoid division by zero
        return np.zeros(3)
    return -MU_EARTH * position / (r ** 3)

def rk4_step(state: np.ndarray, dt: float) -> np.ndarray:
    """
    Runge-Kutta 4th order integration step for orbital dynamics
    state: [x, y, z, vx, vy, vz] in ECI coordinates
    
    Implements: d²r/dt² = -μr / |r|³
    """
    def derivatives(s: np.ndarray) -> np.ndarray:
        pos = s[:3]
        vel = s[3:]
        acc = orbital_acceleration(pos)
        return np.concatenate([vel, acc])
    
    k1 = derivatives(state)
    k2 = derivatives(state + 0.5 * dt * k1)
    k3 = derivatives(state + 0.5 * dt * k2)
    k4 = derivatives(state + dt * k3)
    
    return state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

def propagate_orbit(position: List[float], velocity: List[float], 
                   duration: float, dt: float = 10.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Propagate orbit using RK4 integration in ECI coordinates
    Returns: (positions, velocities, timestamps) arrays
    """
    state = np.array(position + velocity, dtype=np.float64)
    steps = int(duration / dt)
    
    positions = np.zeros((steps, 3))
    velocities = np.zeros((steps, 3))
    timestamps = np.zeros(steps)
    
    for i in range(steps):
        positions[i] = state[:3]
        velocities[i] = state[3:]
        timestamps[i] = i * dt
        state = rk4_step(state, dt)
    
    return positions, velocities, timestamps

def compute_tca_and_distance(pos1_traj: np.ndarray, pos2_traj: np.ndarray, 
                             timestamps: np.ndarray) -> Tuple[float, float, float]:
    """
    Compute Time of Closest Approach (TCA) and minimum distance
    
    Args:
        pos1_traj: Trajectory of object 1 (N x 3)
        pos2_traj: Trajectory of object 2 (N x 3)
        timestamps: Time array (N,)
    
    Returns:
        (tca_time, min_distance, tca_index)
    """
    distances = np.linalg.norm(pos1_traj - pos2_traj, axis=1)
    min_idx = np.argmin(distances)
    
    return timestamps[min_idx], distances[min_idx], min_idx
