#!/usr/bin/env python3
"""Quick test to verify backend starts without errors"""

import sys
import traceback

def test_imports():
    """Test that all imports work"""
    try:
        print("🧪 Testing imports...")
        
        # Test main imports
        from fastapi import FastAPI
        from services.simulation_engine import simulation_engine
        from services.telemetry_service import telemetry_service
        from models.satellite import Satellite
        from models.debris import Debris
        
        print("✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_simulation_engine():
    """Test simulation engine initialization"""
    try:
        print("🧪 Testing simulation engine...")
        
        from services.simulation_engine import simulation_engine
        
        # Test basic properties
        print(f"   - Update interval: {simulation_engine.update_interval}")
        print(f"   - Running: {simulation_engine.running}")
        print(f"   - Gravitational parameter: {simulation_engine.mu}")
        
        print("✅ Simulation engine OK")
        return True
        
    except Exception as e:
        print(f"❌ Simulation engine error: {e}")
        traceback.print_exc()
        return False

def test_telemetry_service():
    """Test telemetry service"""
    try:
        print("🧪 Testing telemetry service...")
        
        from services.telemetry_service import telemetry_service
        
        # Test basic operations
        satellites = telemetry_service.get_all_satellites()
        debris = telemetry_service.get_all_debris()
        status = telemetry_service.get_system_status()
        
        print(f"   - Satellites: {len(satellites)}")
        print(f"   - Debris: {len(debris)}")
        print(f"   - Status keys: {list(status.keys())}")
        
        print("✅ Telemetry service OK")
        return True
        
    except Exception as e:
        print(f"❌ Telemetry service error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Backend Startup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_simulation_engine,
        test_telemetry_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend should start successfully.")
        return 0
    else:
        print("❌ Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())