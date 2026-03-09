"""Fuel consumption model using simplified rocket equation"""
import numpy as np
from typing import List

class FuelModel:
    def __init__(self, isp: float = 300.0, g0: float = 9.81e-3):
        """
        Initialize fuel model
        
        Args:
            isp: Specific impulse in seconds (default 300s for typical thrusters)
            g0: Standard gravity in km/s² (9.81e-3)
        """
        self.isp = isp
        self.g0 = g0
        self.exhaust_velocity = isp * g0  # Effective exhaust velocity
    
    def compute_fuel_consumption(self, delta_v: float, initial_mass: float = 1000.0) -> float:
        """
        Compute fuel consumption using Tsiolkovsky rocket equation
        
        Δm = m₀(1 - e^(-Δv/ve))
        
        Args:
            delta_v: Delta-v magnitude in km/s
            initial_mass: Initial spacecraft mass in kg
        
        Returns:
            Fuel mass consumed in kg
        """
        mass_ratio = np.exp(-delta_v / self.exhaust_velocity)
        final_mass = initial_mass * mass_ratio
        fuel_consumed = initial_mass - final_mass
        
        return fuel_consumed
    
    def compute_fuel_percentage(self, delta_v: float, fuel_capacity: float = 100.0) -> float:
        """
        Compute fuel consumption as percentage of total capacity
        
        Args:
            delta_v: Delta-v magnitude in km/s
            fuel_capacity: Total fuel capacity in kg
        
        Returns:
            Fuel consumed as percentage
        """
        fuel_consumed = self.compute_fuel_consumption(delta_v)
        percentage = (fuel_consumed / fuel_capacity) * 100
        
        return min(percentage, 100.0)
    
    def compute_delta_v_budget(self, fuel_remaining_percent: float, 
                              fuel_capacity: float = 100.0,
                              spacecraft_mass: float = 1000.0) -> float:
        """
        Compute remaining delta-v budget from fuel percentage
        
        Args:
            fuel_remaining_percent: Remaining fuel as percentage
            fuel_capacity: Total fuel capacity in kg
            spacecraft_mass: Dry mass of spacecraft in kg
        
        Returns:
            Remaining delta-v in km/s
        """
        fuel_remaining = (fuel_remaining_percent / 100.0) * fuel_capacity
        initial_mass = spacecraft_mass + fuel_remaining
        
        if fuel_remaining <= 0:
            return 0.0
        
        delta_v = self.exhaust_velocity * np.log(initial_mass / spacecraft_mass)
        return delta_v

# Global instance
fuel_model = FuelModel()
