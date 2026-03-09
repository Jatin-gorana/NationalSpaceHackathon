"""Real-time simulation engine with automatic updates"""
import asyncio
import numpy as np
from typing import List, Dict
from datetime import datetime
from models.satellite import Satellite
from models.debris import Debris
from services.telemetry_service import telemetry_service
from services.collision_detector import collision_detector
from utils.orbital_math import rk4_step
from utils.constants import COLLISION_THRESHOLD

class SimulationEngine:
    def __init__(self, update_interval: float = 1.0):
        self.update_interval = update_interval  # seconds
        self.running = False
        self.task = None
        self.collision_risks = set()
        
    def generate_initial_constellation(self):
        """Generate 50 satellites and 500 debris objects"""
        print("Generating initial constellation...")
        
        # Generate 50 satellites in various orbits
        for i in range(50):
            # LEO orbits: 400-2000 km altitude
            altitude = 400 + (i * 32)  # Spread across LEO
            radius = 6371 + altitude  # Earth radius + altitude
            
            # Distribute around orbit
            angle = (i * 2 * np.pi / 50)
            inclination = np.random.uniform(0, np.pi/6)  # 0-30 degrees
            
            # Position in ECI coordinates
            x = radius * np.cos(angle) * np.cos(inclination)
            y = radius * np.sin(angle) * np.cos(inclination)
            z = radius * np.sin(inclination)
            
            # Circular orbit velocity
            v_mag = np.sqrt(398600.4418 / radius)
            vx = -v_mag * np.sin(angle)
            vy = v_mag * np.cos(angle)
            vz = 0
            
            satellite = Satellite(
                object_id=f"SAT-{i+1:03d}",
                position=[x, y, z],
                velocity=[vx, vy, vz],
                timestamp=datetime.utcnow(),
                assigned_slot=[x, y, z],
                fuel_remaining=np.random.uniform(60, 100),
                status="operational"
            )
            telemetry_service.update_satellite(satellite)
        
        # Generate 500 debris objects
        for i in range(500):
            # Random orbits: 300-2500 km altitude
            altitude = np.random.uniform(300, 2500)
            radius = 6371 + altitude
            
            # Random position
            theta = np.random.uniform(0, 2 * np.pi)
            phi = np.random.uniform(-np.pi/3, np.pi/3)
            
            x = radius * np.cos(theta) * np.cos(phi)
            y = radius * np.sin(theta) * np.cos(phi)
            z = radius * np.sin(phi)
            
            # Orbital velocity with some randomness
            v_mag = np.sqrt(398600.4418 / radius) * np.random.uniform(0.95, 1.05)
            vx = -v_mag * np.sin(theta) + np.random.uniform(-0.1, 0.1)
            vy = v_mag * np.cos(theta) + np.random.uniform(-0.1, 0.1)
            vz = np.random.uniform(-0.2, 0.2)
            
            debris = Debris(
                object_id=f"DEB-{i+1:04d}",
                position=[x, y, z],
                velocity=[vx, vy, vz],
                timestamp=datetime.utcnow(),
                size_estimate=np.random.uniform(0.1, 5.0)
            )
            telemetry_service.update_debris(debris)
        
        print(f"Generated {len(telemetry_service.get_all_satellites())} satellites")
        print(f"Generated {len(telemetry_service.get_all_debris())} debris objects")
    
    async def simulation_loop(self):
        """Main simulation loop - updates every second"""
        print("Starting simulation loop...")
        
        while self.running:
            try:
                # Update all satellites
                satellites = telemetry_service.get_all_satellites()
                for satellite in satellites:
                    # Propagate using RK4
                    state = np.array(satellite.position + satellite.velocity)
                    new_state = rk4_step(state, self.update_interval)
                    
                    satellite.position = new_state[:3].tolist()
                    satellite.velocity = new_state[3:].tolist()
                    satellite.timestamp = datetime.utcnow()
                    
                    telemetry_service.update_satellite(satellite)
                
                # Update all debris
                debris_objects = telemetry_service.get_all_debris()
                for debris in debris_objects:
                    # Propagate using RK4
                    state = np.array(debris.position + debris.velocity)
                    new_state = rk4_step(state, self.update_interval)
                    
                    debris.position = new_state[:3].tolist()
                    debris.velocity = new_state[3:].tolist()
                    debris.timestamp = datetime.utcnow()
                    
                    telemetry_service.update_debris(debris)
                
                # Check for collisions
                self.check_collisions_fast()
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Simulation error: {e}")
                await asyncio.sleep(self.update_interval)
    
    def check_collisions_fast(self):
        """Fast collision check for real-time updates"""
        satellites = telemetry_service.get_all_satellites()
        debris_objects = telemetry_service.get_all_debris()
        
        self.collision_risks.clear()
        
        # Simple distance check (no full propagation for speed)
        for satellite in satellites:
            sat_pos = np.array(satellite.position)
            
            for debris in debris_objects:
                deb_pos = np.array(debris.position)
                distance = np.linalg.norm(sat_pos - deb_pos)
                
                if distance < COLLISION_THRESHOLD * 10:  # 1 km warning threshold
                    self.collision_risks.add(satellite.object_id)
                    satellite.status = "critical" if distance < COLLISION_THRESHOLD else "warning"
                    telemetry_service.update_satellite(satellite)
                    break
            else:
                if satellite.status != "operational":
                    satellite.status = "operational"
                    telemetry_service.update_satellite(satellite)
    
    async def start(self):
        """Start the simulation engine"""
        if not self.running:
            self.running = True
            self.generate_initial_constellation()
            self.task = asyncio.create_task(self.simulation_loop())
            print("Simulation engine started")
    
    async def stop(self):
        """Stop the simulation engine"""
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
            print("Simulation engine stopped")
    
    def get_state(self) -> Dict:
        """Get current simulation state"""
        satellites = telemetry_service.get_all_satellites()
        debris = telemetry_service.get_all_debris()
        
        return {
            "satellites": [
                {
                    "object_id": sat.object_id,
                    "position": sat.position,
                    "velocity": sat.velocity,
                    "fuel_remaining": sat.fuel_remaining,
                    "status": sat.status,
                    "at_risk": sat.object_id in self.collision_risks
                }
                for sat in satellites
            ],
            "debris": [
                {
                    "object_id": deb.object_id,
                    "position": deb.position,
                    "velocity": deb.velocity,
                    "size_estimate": deb.size_estimate
                }
                for deb in debris
            ],
            "collision_risks": list(self.collision_risks),
            "timestamp": datetime.utcnow().isoformat()
        }

# Global instance
simulation_engine = SimulationEngine()
