"""Real-time simulation engine with continuous physics updates"""
import asyncio
import numpy as np
from typing import List, Dict
from datetime import datetime
from scipy.spatial import KDTree
from models.satellite import Satellite
from models.debris import Debris
from services.telemetry_service import telemetry_service
from utils.constants import COLLISION_THRESHOLD

class SimulationEngine:
    def __init__(self, update_interval: float = 0.05):  # 50ms = 20 Hz
        self.update_interval = update_interval
        self.running = False
        self.task = None
        self.mu = 398600.4418  # Earth's gravitational parameter km^3/s^2
        self.collision_risks = set()
        self.threat_count = 0
        
    def generate_initial_constellation(self):
        """Generate 50 satellites and 500 debris objects"""
        print("🛰️  Generating initial constellation...")
        
        # Generate 50 satellites in various LEO orbits
        for i in range(50):
            altitude = 400 + (i * 32)  # 400-2000 km
            radius = 6371 + altitude
            
            # Distribute around orbit
            angle = (i * 2 * np.pi / 50)
            inclination = np.random.uniform(0, np.pi/6)
            
            # Position in ECI coordinates
            x = radius * np.cos(angle) * np.cos(inclination)
            y = radius * np.sin(angle) * np.cos(inclination)
            z = radius * np.sin(inclination)
            
            # Circular orbit velocity
            v_mag = np.sqrt(self.mu / radius)
            vx = -v_mag * np.sin(angle) * np.cos(inclination)
            vy = v_mag * np.cos(angle) * np.cos(inclination)
            vz = v_mag * np.sin(inclination) * 0.1
            
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
            altitude = np.random.uniform(300, 2500)
            radius = 6371 + altitude
            
            # Random position
            theta = np.random.uniform(0, 2 * np.pi)
            phi = np.random.uniform(-np.pi/3, np.pi/3)
            
            x = radius * np.cos(theta) * np.cos(phi)
            y = radius * np.sin(theta) * np.cos(phi)
            z = radius * np.sin(phi)
            
            # Orbital velocity with randomness
            v_mag = np.sqrt(self.mu / radius) * np.random.uniform(0.95, 1.05)
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
        
        print(f"✅ Generated {len(telemetry_service.get_all_satellites())} satellites")
        print(f"✅ Generated {len(telemetry_service.get_all_debris())} debris objects")
    
    def rk4_step(self, position: np.ndarray, velocity: np.ndarray, dt: float) -> tuple:
        """RK4 integration step for orbital dynamics"""
        def acceleration(pos):
            r = np.linalg.norm(pos)
            if r < 1:
                return np.zeros(3)
            return -self.mu * pos / (r ** 3)
        
        # RK4 for velocity and position
        k1_v = acceleration(position)
        k1_p = velocity
        
        k2_v = acceleration(position + 0.5 * dt * k1_p)
        k2_p = velocity + 0.5 * dt * k1_v
        
        k3_v = acceleration(position + 0.5 * dt * k2_p)
        k3_p = velocity + 0.5 * dt * k2_v
        
        k4_v = acceleration(position + dt * k3_p)
        k4_p = velocity + dt * k3_v
        
        new_velocity = velocity + (dt / 6.0) * (k1_v + 2*k2_v + 2*k3_v + k4_v)
        new_position = position + (dt / 6.0) * (k1_p + 2*k2_p + 2*k3_p + k4_p)
        
        return new_position, new_velocity
    
    def propagate_orbits(self):
        """Update all object positions using RK4"""
        # Update satellites
        satellites = telemetry_service.get_all_satellites()
        for satellite in satellites:
            pos = np.array(satellite.position)
            vel = np.array(satellite.velocity)
            
            new_pos, new_vel = self.rk4_step(pos, vel, self.update_interval)
            
            satellite.position = new_pos.tolist()
            satellite.velocity = new_vel.tolist()
            satellite.timestamp = datetime.utcnow()
            
            telemetry_service.update_satellite(satellite)
        
        # Update debris
        debris_objects = telemetry_service.get_all_debris()
        for debris in debris_objects:
            pos = np.array(debris.position)
            vel = np.array(debris.velocity)
            
            new_pos, new_vel = self.rk4_step(pos, vel, self.update_interval)
            
            debris.position = new_pos.tolist()
            debris.velocity = new_vel.tolist()
            debris.timestamp = datetime.utcnow()
            
            telemetry_service.update_debris(debris)
    
    def detect_collisions(self):
        """Fast collision detection using KDTree"""
        satellites = telemetry_service.get_all_satellites()
        debris_objects = telemetry_service.get_all_debris()
        
        if not satellites or not debris_objects:
            return
        
        # Build KDTree for debris positions
        debris_positions = np.array([d.position for d in debris_objects])
        tree = KDTree(debris_positions)
        
        self.collision_risks.clear()
        self.threat_count = 0
        
        # Check each satellite
        for satellite in satellites:
            sat_pos = np.array(satellite.position)
            
            # Find debris within 10 km
            indices = tree.query_ball_point(sat_pos, 10.0)
            
            min_distance = float('inf')
            for idx in indices:
                deb_pos = debris_positions[idx]
                distance = np.linalg.norm(sat_pos - deb_pos)
                min_distance = min(min_distance, distance)
            
            # Update satellite status
            if min_distance < COLLISION_THRESHOLD:  # 100 meters
                satellite.status = "critical"
                self.collision_risks.add(satellite.object_id)
                self.threat_count += 1
            elif min_distance < 1.0:  # 1 km warning
                satellite.status = "warning"
                self.collision_risks.add(satellite.object_id)
            else:
                satellite.status = "operational"
            
            telemetry_service.update_satellite(satellite)
    
    async def simulation_loop(self):
        """Main simulation loop - updates every 50ms"""
        print("🚀 Starting simulation loop (20 Hz)...")
        
        while self.running:
            try:
                # Physics update
                self.propagate_orbits()
                
                # Collision detection
                self.detect_collisions()
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                print(f"❌ Simulation error: {e}")
                await asyncio.sleep(self.update_interval)
    
    async def start(self):
        """Start the simulation engine"""
        if not self.running:
            self.running = True
            self.generate_initial_constellation()
            self.task = asyncio.create_task(self.simulation_loop())
            print("✅ Simulation engine started")
    
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
            print("🛑 Simulation engine stopped")
    
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
            "threats": self.threat_count,
            "timestamp": datetime.utcnow().isoformat()
        }

# Global instance
simulation_engine = SimulationEngine()
