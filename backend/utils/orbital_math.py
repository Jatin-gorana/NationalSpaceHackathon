"""Orbital mechanics utility functions"""
import numpy as np
from typing import List, Tuple
from .constants import MU_EARTH

def distance(pos1: List[float], pos2: List[float]) -> float:
    """Calculate Euclidean distance between two positions"""
    return np.linalg.norm(np.array(pos1) - np.array(pos2))

def orbital_acceleration(position: np.ndarray) -> np.ndarray:
    """Calculate gravitational acceleration at given position"""
    r = np.linalg.norm(position)
    return -MU_EARTH * position / (r ** 3)

def rk4_step(state: np.ndarray, dt: float) -> np.ndarray:
    """
    Runge-Kutta 4th order integration step
    state: [x, y, z, vx, vy, vz]
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
                   duration: float, dt: float = 60.0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Propagate orbit using RK4
    Returns: (positions, velocities) arrays
    """
    state = np.array(position + velocity)
    steps = int(duration / dt)
    
    positions = []
    velocities = []
    
    for _ in range(steps):
        positions.append(state[:3].copy())
        velocities.append(state[3:].copy())
        state = rk4_step(state, dt)
    
    return np.array(positions), np.array(velocities)
