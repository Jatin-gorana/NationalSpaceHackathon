#!/usr/bin/env python3
"""Test script to verify collision scenarios are working"""

import asyncio
import time
from services.simulation_engine import simulation_engine
from services.telemetry_service import telemetry_service

async def test_collision_scenarios():
    print("🧪 Testing Collision Scenarios")
    print("=" * 50)
    
    # Start simulation engine
    print("🚀 Starting simulation engine...")
    await simulation_engine.start()
    
    # Wait a moment for initialization
    await asyncio.sleep(2)
    
    # Check initial state
    satellites = telemetry_service.get_all_satellites()
    debris = telemetry_service.get_all_debris()
    
    print(f"✅ Generated {len(satellites)} satellites")
    print(f"✅ Generated {len(debris)} debris objects")
    
    # Look for collision debris
    collision_debris = [d for d in debris if "IMMEDIATE" in d.object_id or "CROSS" in d.object_id or "CHASE" in d.object_id]
    print(f"⚠️  Created {len(collision_debris)} collision scenarios")
    
    # Monitor for threats over 30 seconds
    print("\n🔍 Monitoring for collision threats...")
    for i in range(30):
        # Run collision detection
        simulation_engine.detect_collisions()
        
        # Check threat count
        threat_count = simulation_engine.threat_count
        at_risk = len(simulation_engine.collision_risks)
        
        print(f"T+{i+1:2d}s: {threat_count} threats, {at_risk} satellites at risk")
        
        if threat_count > 0:
            print(f"🎉 SUCCESS! Collision threats detected after {i+1} seconds")
            
            # Show details
            state = simulation_engine.get_state()
            for collision in state.get("collisions", []):
                print(f"   - {collision['satellite_id']} vs {collision['debris_id']}: {collision['min_distance_meters']:.1f}m")
            break
        
        await asyncio.sleep(1)
    
    if threat_count == 0:
        print("❌ No collision threats detected after 30 seconds")
        print("   This indicates the collision scenarios need adjustment")
    
    # Stop simulation
    await simulation_engine.stop()
    print("\n✅ Test complete")

if __name__ == "__main__":
    asyncio.run(test_collision_scenarios())