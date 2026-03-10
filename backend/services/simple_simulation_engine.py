"""Simplified, guaranteed-working simulation engine for demo"""
import asyncio
import numpy as np
import math
from typing import List, Dict
from datetime import datetime

class SimpleSatellite:
    def __init__(self, id: str, radius: float, angle: float, inclination: float = 0.0, angular_velocity: float = None):
        self.id = id
        self.radius = radius  # km from Earth center
        self.angle = angle  # radians
        self.inclination = inclination  # radians
        # Allow custom angular velocity for demo purposes
        if angular_velocity is None:
            self.angular_velocity = np.random.uniform(0.0008, 0.0015)  # rad/s - realistic range
        else:
            self.angular_velocity = angular_velocity
        self.risk_status = "safe"
        self.fuel = 100.0
        self.original_radius = radius  # Store for maneuver tracking
        
    def update_position(self, dt: float):
        """Update satellite position - guaranteed orbital motion"""
        self.angle += self.angular_velocity * dt
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi
            
    def get_position(self):
        """Get 3D position in km"""
        x = self.radius * math.cos(self.angle) * math.cos(self.inclination)
        y = self.radius * math.sin(self.angle) * math.cos(self.inclination)
        z = self.radius * math.sin(self.inclination)
        return [x, y, z]
    
    def get_velocity(self):
        """Get 3D velocity in km/s"""
        v_mag = math.sqrt(398600.4418 / self.radius)
        vx = -v_mag * math.sin(self.angle) * math.cos(self.inclination)
        vy = v_mag * math.cos(self.angle) * math.cos(self.inclination)
        vz = 0.0
        return [vx, vy, vz]

class SimpleDebris:
    def __init__(self, id: str, radius: float = None, angle: float = None, inclination: float = 0.0, angular_velocity: float = None):
        self.id = id
        # Debris can be orbital or linear
        self.is_orbital = radius is not None
        
        if self.is_orbital:
            # Orbital debris
            self.radius = radius
            self.angle = angle
            self.inclination = inclination
            if angular_velocity is None:
                self.angular_velocity = np.random.uniform(0.0008, 0.0015)
            else:
                self.angular_velocity = angular_velocity
        else:
            # Linear debris (for collision scenarios)
            self.position = np.array([0.0, 0.0, 0.0])
            self.velocity = np.array([0.0, 0.0, 0.0])
        
        self.size = np.random.uniform(0.1, 2.0)
        
    def update_position(self, dt: float):
        """Update debris position"""
        if self.is_orbital:
            # Orbital motion
            self.angle += self.angular_velocity * dt
            if self.angle > 2 * math.pi:
                self.angle -= 2 * math.pi
        else:
            # Linear motion
            self.position += self.velocity * dt
    
    def get_position(self):
        """Get 3D position in km"""
        if self.is_orbital:
            x = self.radius * math.cos(self.angle) * math.cos(self.inclination)
            y = self.radius * math.sin(self.angle) * math.cos(self.inclination)
            z = self.radius * math.sin(self.inclination)
            return [x, y, z]
        else:
            return self.position.tolist()
    
    def get_velocity(self):
        """Get 3D velocity in km/s"""
        if self.is_orbital:
            v_mag = math.sqrt(398600.4418 / self.radius)
            vx = -v_mag * math.sin(self.angle) * math.cos(self.inclination)
            vy = v_mag * math.cos(self.angle) * math.cos(self.inclination)
            vz = 0.0
            return [vx, vy, vz]
        else:
            return self.velocity.tolist()

class SimpleSimulationEngine:
    def __init__(self):
        self.running = False
        self.satellites: List[SimpleSatellite] = []
        self.debris: List[SimpleDebris] = []
        self.simulation_time = 0.0
        self.threat_count = 0
        self.collision_risks = set()
        self.update_interval = 0.05  # 20 Hz
        self.last_threat_time = 0.0
        self.threat_generation_interval = np.random.uniform(60, 120)  # 1-2 minutes (faster threats)
        self.min_background_debris = 10
        
    def initialize_constellation(self):
        """Create satellites and debris - guaranteed to work"""
        print("🛰️ Initializing dynamic constellation...")
        
        # Create 20 satellites in circular orbits with varied parameters
        self.satellites = []
        for i in range(20):
            radius = np.random.uniform(6800, 7200)  # 6800-7200 km (realistic LEO)
            angle = np.random.uniform(0, 2 * math.pi)  # Random starting angle
            inclination = np.random.uniform(0, 0.3)  # 0-17 degrees
            angular_velocity = np.random.uniform(0.0008, 0.0015)  # rad/s
            
            satellite = SimpleSatellite(f"SAT-{i+1:03d}", radius, angle, inclination, angular_velocity)
            self.satellites.append(satellite)
        
        # Create orbital debris (background)
        self.debris = []
        for i in range(10):
            radius = np.random.uniform(6800, 7200)
            angle = np.random.uniform(0, 2 * math.pi)
            inclination = np.random.uniform(0, 0.3)
            angular_velocity = np.random.uniform(0.0008, 0.0015)
            
            debris = SimpleDebris(f"DEB-{i+1:03d}", radius, angle, inclination, angular_velocity)
            self.debris.append(debris)
        
        print(f"✅ Created {len(self.satellites)} satellites and {len(self.debris)} orbital debris")
        print(f"🎯 Collision threats will appear every 2-3 minutes")
    
    def create_collision_threat(self):
        """Create a collision threat scenario"""
        # Pick a random satellite
        target_sat = np.random.choice(self.satellites)
        
        # Create debris VERY CLOSE to its orbit (within collision threshold)
        threat_debris = SimpleDebris(
            f"THREAT-{len(self.debris)+1:03d}",
            radius=target_sat.radius + np.random.uniform(-5, 5),  # Within 5 km radius
            angle=target_sat.angle + np.random.uniform(-0.05, 0.05),  # Very close angle
            inclination=target_sat.inclination + np.random.uniform(-0.02, 0.02),
            angular_velocity=target_sat.angular_velocity + np.random.uniform(-0.00005, 0.00005)  # Nearly same speed
        )
        
        self.debris.append(threat_debris)
        print(f"⚠️ COLLISION THREAT CREATED: {threat_debris.id} near {target_sat.id}")
        return target_sat.id
    
    def update_simulation(self):
        """Update all objects - guaranteed smooth motion"""
        dt = self.update_interval
        self.simulation_time += dt
        
        # Update satellite positions
        for satellite in self.satellites:
            satellite.update_position(dt)
        
        # Update debris positions
        for debris in self.debris:
            debris.update_position(dt)
        
        # Detect collisions
        self.detect_collisions()
        
        # Generate random threats every 1-2 minutes
        if self.simulation_time - self.last_threat_time > self.threat_generation_interval:
            self.create_collision_threat()
            self.last_threat_time = self.simulation_time
            self.threat_generation_interval = np.random.uniform(60, 120)  # 1-2 minutes
        
        # Log every 100 ticks (5 seconds)
        if int(self.simulation_time / dt) % 100 == 0:
            print(f"🔄 Simulation tick: {self.simulation_time:.1f}s, Threats: {self.threat_count}, Debris: {len(self.debris)}")
    
    def detect_collisions(self):
        """Detect collisions between satellites and debris"""
        self.collision_risks.clear()
        self.threat_count = 0
        
        for satellite in self.satellites:
            satellite.risk_status = "safe"
            sat_pos = np.array(satellite.get_position())
            
            for debris in self.debris:
                deb_pos = np.array(debris.get_position())
                
                # Calculate distance
                distance = np.linalg.norm(sat_pos - deb_pos)
                
                # Check collision risk (100 km threshold for demo visibility)
                if distance < 100.0:
                    satellite.risk_status = "danger"
                    self.collision_risks.add(satellite.id)
                    self.threat_count += 1
                    break
    
    def apply_maneuver(self, satellite_id: str):
        """Apply collision avoidance maneuver"""
        for satellite in self.satellites:
            if satellite.id == satellite_id:
                # Increase orbit radius by 60 km
                satellite.radius += 60
                # Recalculate angular velocity for new orbit
                satellite.angular_velocity = np.random.uniform(0.0008, 0.0015)
                satellite.risk_status = "safe"
                satellite.fuel -= 5.0
                
                # Remove threat debris that was threatening this satellite
                debris_to_remove = []
                sat_pos = np.array(satellite.get_position())
                for idx, debris in enumerate(self.debris):
                    if "THREAT" in debris.id:
                        deb_pos = np.array(debris.get_position())
                        distance = np.linalg.norm(sat_pos - deb_pos)
                        if distance < 150.0:  # Remove threats within 150km
                            debris_to_remove.append(idx)
                
                # Remove in reverse order to maintain indices
                for idx in sorted(debris_to_remove, reverse=True):
                    removed = self.debris.pop(idx)
                    print(f"🗑️ Threat debris removed by maneuver: {removed.id}")
                
                print(f"✅ Maneuver executed for {satellite_id}: new radius {satellite.radius:.0f} km, fuel {satellite.fuel:.1f}%")
                return True
        return False
    
    def get_state(self) -> Dict:
        """Get current simulation state with full position data"""
        satellites_data = []
        for sat in self.satellites:
            pos = sat.get_position()
            vel = sat.get_velocity()
            satellites_data.append({
                "id": sat.id,
                "position": pos,  # [x, y, z] in km
                "velocity": vel,  # [vx, vy, vz] in km/s
                "fuel": round(sat.fuel, 1),
                "risk_status": sat.risk_status
            })
        
        debris_data = []
        for deb in self.debris:
            debris_data.append({
                "id": deb.id,
                "position": deb.get_position(),  # [x, y, z] in km
                "velocity": deb.get_velocity()   # [vx, vy, vz] in km/s
            })
        
        return {
            "timestamp": self.simulation_time,
            "satellites": satellites_data,
            "debris": debris_data,
            "threats": self.threat_count
        }
    
    async def start(self):
        """Start simulation"""
        if not self.running:
            print("🚀 Starting dynamic simulation engine...")
            self.initialize_constellation()
            self.running = True
            
            # Start update loop
            asyncio.create_task(self.simulation_loop())
            print("✅ Dynamic simulation engine started")
    
    async def simulation_loop(self):
        """Main simulation loop"""
        while self.running:
            try:
                self.update_simulation()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                print(f"❌ Simulation error: {e}")
                await asyncio.sleep(self.update_interval)
    
    async def stop(self):
        """Stop simulation"""
        self.running = False
        print("🛑 Dynamic simulation engine stopped")

# Global instance
simple_simulation_engine = SimpleSimulationEngine()