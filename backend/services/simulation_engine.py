"""Real-time simulation engine with continuous physics updates"""
import asyncio
import numpy as np
from typing import List, Dict
from datetime import datetime
from scipy.spatial import KDTree
from models.satellite import Satellite
from models.debris import Debris
from services.telemetry_service import telemetry_service
from utils.constants import (
    COLLISION_THRESHOLD, LOW_FUEL_THRESHOLD, SLOT_TOLERANCE,
    THRUSTER_COOLDOWN, MANEUVER_EXECUTION_TOLERANCE
)

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
        self.simulation_time = 0.0  # Simulation time in seconds
        self.maneuvers_executed = 0
        self.satellites_in_graveyard = set()
        
    def generate_initial_constellation(self):
        """Generate 50 satellites and 100 debris objects with persistent collision scenarios"""
        print("🛰️  Generating initial constellation...")
        
        # Generate 50 satellites in various LEO orbits (optimized)
        satellites_data = []
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
        
        print(f"✅ Generated 50 satellites")
        
        # Generate only 100 debris objects for faster startup (reduced from 500)
        debris_data = []
        for i in range(100):
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
        
        print(f"✅ Generated 100 debris objects (optimized for faster startup)")
        
        # Create PERSISTENT collision scenarios for 15 satellites
        satellites = telemetry_service.get_all_satellites()
        
        print("⚠️  Creating IMMEDIATE collision scenarios...")
        
        # Strategy 1: Debris VERY close to satellites (immediate threats)
        for i in range(min(8, len(satellites))):
            sat = satellites[i]
            sat_pos = np.array(sat.position)
            sat_vel = np.array(sat.velocity)
            
            # Place debris VERY close (within 5 km) on collision course
            # Random direction around satellite
            angle = np.random.uniform(0, 2 * np.pi)
            distance = np.random.uniform(2.0, 8.0)  # 2-8 km away
            
            # Direction vector
            direction = np.array([np.cos(angle), np.sin(angle), np.random.uniform(-0.3, 0.3)])
            direction = direction / np.linalg.norm(direction)
            
            # Place debris close to satellite
            collision_debris_pos = sat_pos + direction * distance
            
            # Velocity towards satellite (collision course)
            to_satellite = sat_pos - collision_debris_pos
            to_satellite = to_satellite / np.linalg.norm(to_satellite)
            
            # Speed similar to satellite but on collision course
            collision_speed = np.linalg.norm(sat_vel) * 0.95
            collision_debris_vel = to_satellite * collision_speed + sat_vel * 0.1
            
            collision_debris = Debris(
                object_id=f"DEB-IMMEDIATE-{i+1:03d}",
                position=collision_debris_pos.tolist(),
                velocity=collision_debris_vel.tolist(),
                timestamp=datetime.utcnow(),
                size_estimate=2.0
            )
            telemetry_service.update_debris(collision_debris)
        
        # Strategy 2: Debris on crossing orbital planes (4 satellites)
        for i in range(8, min(12, len(satellites))):
            sat = satellites[i]
            sat_pos = np.array(sat.position)
            sat_vel = np.array(sat.velocity)
            
            # Create debris with perpendicular velocity (crossing orbit)
            radial = sat_pos / np.linalg.norm(sat_pos)
            perpendicular = np.cross(sat_vel, radial)
            perpendicular = perpendicular / np.linalg.norm(perpendicular)
            
            # Place debris close but on crossing path
            collision_debris_pos = sat_pos + perpendicular * 3.0  # 3 km offset
            collision_debris_vel = sat_vel * 0.8 + perpendicular * 2.0  # Crossing velocity
            
            collision_debris = Debris(
                object_id=f"DEB-CROSS-{i+1:03d}",
                position=collision_debris_pos.tolist(),
                velocity=collision_debris_vel.tolist(),
                timestamp=datetime.utcnow(),
                size_estimate=1.5
            )
            telemetry_service.update_debris(collision_debris)
        
        # Strategy 3: Debris chasing from behind (3 satellites)
        for i in range(12, min(15, len(satellites))):
            sat = satellites[i]
            sat_pos = np.array(sat.position)
            sat_vel = np.array(sat.velocity)
            
            # Place debris behind, moving faster (catching up)
            collision_debris_pos = sat_pos - sat_vel * 1.5  # 1.5 seconds behind
            collision_debris_vel = sat_vel * 1.15  # 15% faster (catching up quickly)
            
            collision_debris = Debris(
                object_id=f"DEB-CHASE-{i+1:03d}",
                position=collision_debris_pos.tolist(),
                velocity=collision_debris_vel.tolist(),
                timestamp=datetime.utcnow(),
                size_estimate=2.5
            )
            telemetry_service.update_debris(collision_debris)
            
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
        print(f"⚠️  Created 15 IMMEDIATE collision scenarios (within 2-8 km)")
        print("🔥 Collision threats should appear within 10-30 seconds!")
    
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
            
            # Find debris within 15 km (increased from 10 km)
            indices = tree.query_ball_point(sat_pos, 15.0)
            
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
            elif min_distance < 5.0:  # 5 km warning (increased from 1 km)
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
    
    def execute_scheduled_maneuvers(self):
        """Execute maneuvers that are due for execution"""
        from services.maneuver_planner import maneuver_planner
        
        satellites = telemetry_service.get_all_satellites()
        
        for satellite in satellites:
            # Skip satellites in graveyard orbit
            if satellite.status == "graveyard" or satellite.status == "decommissioned":
                continue
            
            # Get scheduled maneuvers
            scheduled = getattr(satellite, 'scheduled_maneuvers', [])
            
            if not scheduled:
                continue
            
            # Check for maneuvers ready to execute
            for maneuver in scheduled[:]:  # Copy list to allow modification
                exec_time = maneuver.get("execution_time_seconds", 0)
                
                # Check if maneuver is due (within tolerance)
                if abs(self.simulation_time - exec_time) <= MANEUVER_EXECUTION_TOLERANCE:
                    # Check thruster cooldown
                    time_since_last = self.simulation_time - satellite.last_maneuver_time
                    
                    if time_since_last >= THRUSTER_COOLDOWN:
                        # Execute maneuver
                        success = self.apply_maneuver(
                            satellite.object_id,
                            maneuver["delta_v"]
                        )
                        
                        if success:
                            # Update last maneuver time
                            satellite.last_maneuver_time = self.simulation_time
                            
                            # Remove from schedule
                            scheduled.remove(maneuver)
                            satellite.scheduled_maneuvers = scheduled
                            
                            # Update status
                            if maneuver.get("maneuver_type") == "graveyard_orbit":
                                satellite.status = "graveyard"
                                self.satellites_in_graveyard.add(satellite.object_id)
                            else:
                                satellite.status = "maneuvering"
                            
                            telemetry_service.update_satellite(satellite)
                            self.maneuvers_executed += 1
                            
                            print(f"✅ Executed {maneuver.get('maneuver_type', 'maneuver')} for {satellite.object_id}")
                    else:
                        print(f"⏳ Thruster cooldown: {THRUSTER_COOLDOWN - time_since_last:.0f}s remaining for {satellite.object_id}")
    
    def check_orbit_recovery_needed(self):
        """Check if satellites need orbit recovery maneuvers"""
        from services.maneuver_planner import maneuver_planner
        from utils.orbital_math import distance
        
        satellites = telemetry_service.get_all_satellites()
        
        for satellite in satellites:
            # Skip satellites in graveyard or already recovering
            if satellite.status in ["graveyard", "decommissioned"]:
                continue
            
            # Skip if already has scheduled maneuvers
            if getattr(satellite, 'scheduled_maneuvers', []):
                continue
            
            # Check deviation from assigned slot
            deviation = distance(satellite.position, satellite.assigned_slot)
            
            # If deviation > tolerance and not in collision risk, schedule recovery
            if deviation > SLOT_TOLERANCE and satellite.status != "critical":
                recovery_maneuver = maneuver_planner.plan_orbit_recovery(
                    satellite.object_id,
                    satellite.position,
                    satellite.velocity,
                    satellite.assigned_slot,
                    satellite.fuel_remaining,
                    execution_delay=self.simulation_time + 120.0  # Execute in 2 minutes
                )
                
                if recovery_maneuver:
                    # Add to satellite's schedule
                    if not hasattr(satellite, 'scheduled_maneuvers'):
                        satellite.scheduled_maneuvers = []
                    satellite.scheduled_maneuvers.append(recovery_maneuver)
                    satellite.in_recovery = True
                    telemetry_service.update_satellite(satellite)
                    print(f"📍 Scheduled orbit recovery for {satellite.object_id} (deviation: {deviation:.2f} km)")
    
    def check_low_fuel_satellites(self):
        """Check for low fuel satellites and move to graveyard orbit"""
        from services.maneuver_planner import maneuver_planner
        
        satellites = telemetry_service.get_all_satellites()
        
        for satellite in satellites:
            # Skip if already in graveyard
            if satellite.object_id in self.satellites_in_graveyard:
                continue
            
            # Check if fuel is critically low
            if satellite.fuel_remaining <= LOW_FUEL_THRESHOLD:
                print(f"⚠️ Low fuel detected for {satellite.object_id}: {satellite.fuel_remaining:.1f}%")
                
                # Plan graveyard orbit maneuver
                graveyard_maneuver = maneuver_planner.plan_graveyard_orbit(
                    satellite.object_id,
                    satellite.position,
                    satellite.velocity,
                    satellite.fuel_remaining
                )
                
                if graveyard_maneuver:
                    # Add to satellite's schedule (high priority)
                    if not hasattr(satellite, 'scheduled_maneuvers'):
                        satellite.scheduled_maneuvers = []
                    
                    # Clear other maneuvers and add graveyard maneuver
                    satellite.scheduled_maneuvers = [graveyard_maneuver]
                    graveyard_maneuver["execution_time_seconds"] = self.simulation_time + 30.0
                    
                    telemetry_service.update_satellite(satellite)
                    print(f"🪦 Scheduled graveyard orbit for {satellite.object_id}")
    
    async def simulation_loop(self):
        """Main simulation loop - updates every 50ms"""
        print("🚀 Starting simulation loop (20 Hz)...")
        
        iteration = 0
        
        while self.running:
            try:
                # Update simulation time
                self.simulation_time += self.update_interval
                
                # Physics update (every iteration)
                self.propagate_orbits()
                
                # Collision detection (every iteration)
                self.detect_collisions()
                
                # Execute scheduled maneuvers (every iteration)
                self.execute_scheduled_maneuvers()
                
                # Conjunction prediction (every 10 seconds = 200 iterations)
                if iteration % 200 == 0:
                    await self.predict_conjunctions()
                
                # Check for orbit recovery needs (every 30 seconds = 600 iterations)
                if iteration % 600 == 0:
                    self.check_orbit_recovery_needed()
                
                # Check for low fuel satellites (every 60 seconds = 1200 iterations)
                if iteration % 1200 == 0:
                    self.check_low_fuel_satellites()
                
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
            print("🚀 Starting simulation engine...")
            
            # Generate constellation asynchronously to not block startup
            asyncio.create_task(self.generate_constellation_async())
            
            # Start simulation loop immediately
            self.task = asyncio.create_task(self.simulation_loop())
            print("✅ Simulation engine started (constellation generating in background)")
    
    async def generate_constellation_async(self):
        """Generate constellation asynchronously"""
        await asyncio.sleep(0.1)  # Let other tasks start first
        self.generate_initial_constellation()
    
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
                    "at_risk": sat.object_id in self.collision_risks,
                    "scheduled_maneuvers": getattr(sat, 'scheduled_maneuvers', []),
                    "in_recovery": getattr(sat, 'in_recovery', False)
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
            "timestamp": datetime.utcnow().isoformat(),
            "simulation_time": round(self.simulation_time, 2),
            "maneuvers_executed": self.maneuvers_executed,
            "satellites_in_graveyard": len(self.satellites_in_graveyard)
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
