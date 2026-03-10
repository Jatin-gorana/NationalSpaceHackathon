#!/usr/bin/env python3
"""
Quick verification that the ACM system is demo-ready
"""
import requests
import json
import time

def check_backend():
    """Check if backend is running and responsive"""
    print("🔍 Checking backend...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy")
            print(f"   - Simulation running: {data.get('simulation_running', False)}")
            return True
        else:
            print(f"❌ Backend unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def check_simulation_data():
    """Check if simulation is generating data"""
    print("🛰️ Checking simulation data...")
    
    try:
        response = requests.get("http://localhost:8000/", timeout=3)
        if response.status_code == 200:
            data = response.json()
            sim_data = data.get('simulation', {})
            
            satellites = sim_data.get('satellites', 0)
            debris = sim_data.get('debris', 0)
            threats = sim_data.get('threats', 0)
            
            print(f"✅ Simulation data:")
            print(f"   - Satellites: {satellites}")
            print(f"   - Debris: {debris}")
            print(f"   - Threats: {threats}")
            
            if satellites > 0 and debris > 0:
                print("✅ Simulation has objects")
                return True
            else:
                print("❌ Simulation has no objects")
                return False
        else:
            print(f"❌ Cannot get simulation data: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Simulation data check failed: {e}")
        return False

def check_collision_detection():
    """Check if collision detection is working"""
    print("⚠️ Checking collision detection...")
    
    try:
        response = requests.get("http://localhost:8000/debug/force-collisions", timeout=3)
        if response.status_code == 200:
            data = response.json()
            
            total_sats = data.get('total_satellites', 0)
            at_risk = data.get('satellites_at_risk', 0)
            threats = data.get('threat_count', 0)
            
            print(f"✅ Collision detection:")
            print(f"   - Total satellites: {total_sats}")
            print(f"   - At risk: {at_risk}")
            print(f"   - Threat count: {threats}")
            
            return True
        else:
            print(f"❌ Collision detection check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Collision detection error: {e}")
        return False

def main():
    """Run verification checks"""
    print("🚀 ACM Demo Readiness Check")
    print("=" * 40)
    
    checks = [
        ("Backend Health", check_backend),
        ("Simulation Data", check_simulation_data),
        ("Collision Detection", check_collision_detection)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n{name}:")
        if check_func():
            passed += 1
        print("-" * 20)
    
    print(f"\n📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 System is DEMO READY!")
        print("\nNext steps:")
        print("1. Start frontend: cd frontend && npm run dev")
        print("2. Open browser to http://localhost:5173")
        print("3. Watch satellites orbit and collision detection!")
    else:
        print("❌ System needs attention before demo")
    
    return passed == total

if __name__ == "__main__":
    main()