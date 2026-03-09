"""Test script for orbital physics simulation and collision detection"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def test_simulation():
    print("=" * 80)
    print("ACM Orbital Physics Simulation Test")
    print("=" * 80)
    
    # 1. Add test satellites
    print("\n1. Adding test satellites...")
    satellites = [
        {
            "object_id": "SAT-001",
            "type": "satellite",
            "position": [7000.0, 0.0, 0.0],
            "velocity": [0.0, 7.5, 0.0],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        {
            "object_id": "SAT-002",
            "type": "satellite",
            "position": [6900.0, 500.0, 100.0],
            "velocity": [0.1, 7.6, 0.05],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    ]
    
    for sat in satellites:
        response = requests.post(f"{BASE_URL}/telemetry", json=sat)
        print(f"   Added {sat['object_id']}: {response.status_code}")
    
    # 2. Add test debris
    print("\n2. Adding test debris objects...")
    debris_list = [
        {
            "object_id": "DEB-001",
            "type": "debris",
            "position": [7000.0, 50.0, 10.0],
            "velocity": [0.05, 7.48, 0.01],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        {
            "object_id": "DEB-002",
            "type": "debris",
            "position": [6950.0, 300.0, 80.0],
            "velocity": [0.08, 7.55, 0.03],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        {
            "object_id": "DEB-003",
            "type": "debris",
            "position": [7100.0, -200.0, 50.0],
            "velocity": [-0.02, 7.45, 0.02],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    ]
    
    for deb in debris_list:
        response = requests.post(f"{BASE_URL}/telemetry", json=deb)
        print(f"   Added {deb['object_id']}: {response.status_code}")
    
    # 3. Run simulation step
    print("\n3. Running orbital physics simulation...")
    print("   Physics: ECI coordinates, RK4 integration, 10s timestep")
    print("   Optimization: KDTree spatial indexing, 50km search radius")
    
    sim_request = {"simulation_time_step": 24.0}
    response = requests.post(f"{BASE_URL}/simulate/step", json=sim_request)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n   ✓ Simulation completed successfully")
        print(f"\n   Physics Model:")
        print(f"     - Coordinate System: {result['physics_model']['coordinate_system']}")
        print(f"     - Integration: {result['physics_model']['integration_method']}")
        print(f"     - Timestep: {result['physics_model']['timestep_seconds']}s")
        
        print(f"\n   Collision Detection:")
        print(f"     - Algorithm: {result['collision_detection']['algorithm']}")
        print(f"     - Search Radius: {result['collision_detection']['search_radius_km']} km")
        print(f"     - Threshold: {result['collision_detection']['collision_threshold_meters']} m")
        print(f"     - Total Collisions: {result['collision_detection']['total_collisions']}")
        print(f"     - Critical: {result['collision_detection']['critical_collisions']}")
        print(f"     - Warnings: {result['collision_detection']['warning_collisions']}")
        
        print(f"\n   System Summary:")
        print(f"     - Satellites: {result['system_summary']['total_satellites']}")
        print(f"     - Debris: {result['system_summary']['total_debris']}")
        print(f"     - Satellites at Risk: {result['system_summary']['satellites_at_risk']}")
        
        # Display collision details
        if result['predicted_collisions']:
            print(f"\n4. Collision Alerts:")
            for i, collision in enumerate(result['predicted_collisions'][:5], 1):
                print(f"\n   Alert #{i}:")
                print(f"     Satellite: {collision['satellite_id']}")
                print(f"     Debris: {collision['debris_id']}")
                print(f"     TCA: {collision['tca_hours']:.3f} hours")
                print(f"     Min Distance: {collision['min_distance_meters']:.2f} meters")
                print(f"     Severity: {collision['severity'].upper()}")
        else:
            print(f"\n4. No collisions detected ✓")
        
        # Display satellite states
        print(f"\n5. Satellite States:")
        for sat_state in result['satellite_states']:
            print(f"\n   {sat_state['object_id']}:")
            print(f"     Current Pos: {[f'{x:.2f}' for x in sat_state['current_position']]}")
            print(f"     Predicted Pos: {[f'{x:.2f}' for x in sat_state['predicted_position']]}")
            print(f"     Trajectory Points: {sat_state['trajectory_points']}")
        
        # Save full result
        with open('simulation_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n   Full results saved to simulation_result.json")
        
    else:
        print(f"   ✗ Simulation failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    try:
        test_simulation()
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to ACM backend.")
        print("Please start the server with: uvicorn main:app --reload")
