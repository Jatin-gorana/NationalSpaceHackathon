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
        self.predicted_collisions = []  # Store predicted collisions with full details
        self.last_prediction_time = 0  # Track when we last ran prediction
        
    def generate_initial_constellation(self):
        """Generate 50 satellites and 500 debris objects with persistent collision scenarios"""
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
        
        # Create PERSISTENT collision scenarios for 15 satellites
        satellites = telemetry_service.get_all_satellites()
        
        print("⚠️  Creating persistent collision scenarios...")
        
        # Strategy 1: Debris on converging orbits (5 satellites)
        for i in range(min(5, len(satellites))):
            sat = satellites[i]
            sat_pos = np.array(sat.position)
            sat_vel = np.array(sat.velocity)
            
            # Place debris on converging orbit (opposite direction, same altitude)
            collision_debris_pos = sat_pos + sat_vel * 2.0  # 2 seconds ahead
            collision_debris_vel = -sat_vel * 0.98  # Opposite direction, slightly slower
            
            collision_debris = Debris(
                object_id=f"DEB-CONVERGE-{i+1:03d}",
                position=collision_debris_pos.tolist(),
                velocity=collision_debris_vel.tolist(),
                timestamp=datetime.utcnow(),
                size_estimate=2.0
            )
            telemetry_service.update_debris(collision_debris)
        
        # Strategy 2: Debris on crossing orbital planes (5 satellites)
        for i in range(5, min(10, len(satellites))):
            sat = satellites[i]
            sat_pos = np.array(sat.position)
            sat_vel = np.array(sat.velocity)
            
            # Create debris with perpendicular velocity (crossing orbit)
            radial = sat_pos / np.linalg.norm(sat_pos)
            perpendicular = np.cross(sat_vel, radial)
            perpendicular = perpendicular / np.linalg.norm(perpendicular)
            
            # Place debris on crossing path
            collision_debris_pos = sat_pos + perpendicular * 5.0  # 5 km offset
            collision_debris_vel = sat_vel + perpendicular * 0.5  # Crossing velocity
            
            collision_debris = Debris(
                object_id=f"DEB-CROSS-{i+1:03d}",
                position=collision_debris_pos.tolist(),
                velocity=collision_debris_vel.tolist(),
                timestamp=datetime.utcnow(),
                size_estimate=1.5
            )
            telemetry_service.update_debris(collision_debris)
        
        # Strategy 3: Debris on same orbit, catching up (5 satellites)
        for i in range(10, min(15, len(satellites))):
            sat = satellites[i]
            sat_pos = np.array(sat.position)
            sat_vel = np.array(sat.velocity)
            
            # Place debris behind, moving faster
            collision_debris_pos = sat_pos - sat_vel * 3.0  # 3 seconds behind
            collision_debris_vel = sat_vel * 1.02  # 2% faster (catching up)
            
            collision_debris = Debris(
                object_id=f"DEB-CHASE-{i+1:03d}",
                position=collision_debris_pos.tolist(),
                velocity=collision_debris_vel.tolist(),
                timestamp=datetime.utcnow(),
                size_estimate=2.5
            )
            telemetry_service.update_debris(collision_debris)
        
        print(f"✅ Generated {len(telemetry_service.get_all_satellites())} satellites")
        print(f"✅ Generated {len(telemetry_service.get_all_debris())} debris objects")
        print(f"⚠️  Created 15 persistent collision scenarios (converging, crossing, chasing)")
    
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
        """Fast collision detection using KDTree with enhanced details"""
        satellites = telemetry_service.get_all_satellites()
        debris_objects = telemetry_service.get_all_debris()
        
        if not satellites or not debris_objects:
            return
        
        # Build KDTree for debris positions
        debris_positions = np.array([d.position for d in debris_objects])
        tree = KDTree(debris_positions)
        
        self.collision_risks.clear()
        self.threat_count = 0
        collision_details = {}  # Store detailed collision info
        
        # Check each satellite
        for satellite in satellites:
            sat_pos = np.array(satellite.position)
            
            # Find debris within 10 km
            indices = tree.query_ball_point(sat_pos, 10.0)
            
            min_distance = float('inf')
            closest_debris_id = None
            
            for idx in indices:
                deb_pos = debris_positions[idx]
                distance = np.linalg.norm(sat_pos - deb_pos)
                if distance < min_distance:
                    min_distance = distance
                    closest_debris_id = debris_objects[idx].object_id
            
            # Update satellite status and store collision details
            if min_distance < COLLISION_THRESHOLD:  # 100 meters
                satellite.status = "critical"
                self.collision_risks.add(satellite.object_id)
                self.threat_count += 1
                collision_details[satellite.object_id] = {
                    "debris_id": closest_debris_id,
                    "min_distance_km": min_distance,
                    "min_distance_meters": min_distance * 1000,
                    "severity": "critical"
                }
            elif min_distance < 1.0:  # 1 km warning
                satellite.status = "warning"
                self.collision_risks.add(satellite.object_id)
                collision_details[satellite.object_id] = {
                    "debris_id": closest_debris_id,
                    "min_distance_km": min_distance,
                    "min_distance_meters": min_distance * 1000,
                    "severity": "warning"
                }
            else:
                satellite.status = "operational"
            
            telemetry_service.update_satellite(satellite)
        
        # Store collision details for WebSocket broadcast
        self.current_collision_details = collision_details
    
    async def predict_conjunctions(self):
        """Run conjunction prediction every 10 seconds"""
        from services.collision_detector import collision_detector
        
        try:
            # Run full conjunction prediction (24 hours ahead)
            predicted = collision_detector.detect_collisions(hours_ahead=24)
            self.predicted_collisions = predicted
            print(f"🔮 Predicted {len(predicted)} conjunctions in next 24 hours")
        except Exception as e:
            print(f"❌ Conjunction prediction error: {e}")
            self.predicted_collisions = []
    
    async def simulation_loop(self):
        """Main simulation loop - updates every 50ms"""
        print("🚀 Starting simulation loop (20 Hz)...")
        
        iteration = 0
        
        while self.running:
            try:
                # Physics update (every iteration)
                self.propagate_orbits()
                
                # Collision detection (every iteration)
                self.detect_collisions()
                
                # Conjunction prediction (every 10 seconds = 200 iterations)
                if iteration % 200 == 0:
                    await self.predict_conjunctions()
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                iteration += 1
                
            except Exception as e:
                print(f"❌ Simulation error: {e}")
                import traceback
                traceback.print_exc()
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
        """Get current simulation state with enhanced collision details"""
        satellites = telemetry_service.get_all_satellites()
        debris = telemetry_service.get_all_debris()
        
        # Build collision list with full details
        collisions = []
        if hasattr(self, 'current_collision_details'):
            for sat_id, details in self.current_collision_details.items():
                collisions.append({
                    "satellite_id": sat_id,
                    "debris_id": details.get("debris_id"),
                    "min_distance_km": details.get("min_distance_km"),
                    "min_distance_meters": details.get("min_distance_meters"),
                    "severity": details.get("severity"),
                    "tca_hours": 0.0  # Current collision (TCA = now)
                })
        
        # Add predicted collisions
        if hasattr(self, 'predicted_collisions'):
            for pred in self.predicted_collisions[:10]:  # Top 10 predicted
                # Only add if not already in current collisions
                if not any(c['satellite_id'] == pred['satellite_id'] for c in collisions):
                    collisions.append(pred)
        
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
            "collisions": collisions,  # Enhanced with full details
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def apply_maneuver(self, satellite_id: str, delta_v: List[float]):
        """Apply a maneuver to a satellite (change velocity)"""
        satellites = telemetry_service.get_all_satellites()
        for sat in satellites:
            if sat.object_id == satellite_id:
                # Apply delta-v to velocity
                sat.velocity = [
                    sat.velocity[0] + delta_v[0],
                    sat.velocity[1] + delta_v[1],
                    sat.velocity[2] + delta_v[2]
                ]
                
                # Deduct fuel (simplified: 1 m/s costs 0.1% fuel)
                delta_v_mag = np.linalg.norm(delta_v)
                fuel_cost = delta_v_mag * 0.1
                sat.fuel_remaining = max(0, sat.fuel_remaining - fuel_cost)
                
                telemetry_service.update_satellite(sat)
                print(f"✅ Applied maneuver to {satellite_id}: ΔV={delta_v}, Fuel remaining: {sat.fuel_remaining:.1f}%")
                return True
        return False

# Global instance
simulation_engine = SimulationEngine()
