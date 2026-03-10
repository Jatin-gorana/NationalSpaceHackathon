#!/usr/bin/env python3
"""
Test script to verify the full ACM system is working correctly
"""
import asyncio
import websockets
import json
import requests
import time

async def test_websocket():
    """Test WebSocket connection and data flow"""
    print("🔌 Testing WebSocket connection...")
    
    try:
        uri = "ws://localhost:8000/ws/simulation"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Receive a few messages
            for i in range(5):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    
                    print(f"📡 Message {i+1}:")
                    print(f"  - Timestamp: {data.get('timestamp', 'N/A')}")
                    print(f"  - Satellites: {len(data.get('satellites', []))}")
                    print(f"  - Debris: {len(data.get('debris', []))}")
                    print(f"  - Threats: {data.get('threats', 0)}")
                    
                    # Check first satellite data structure
                    if data.get('satellites'):
                        sat = data['satellites'][0]
                        print(f"  - Sample satellite: {sat.get('id')} at {sat.get('position')} with status {sat.get('risk_status')}")
                    
                    await asyncio.sleep(0.1)
                    
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for message")
                    break
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    break
                    
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False
    
    print("✅ WebSocket test completed successfully!")
    return True

def test_http_endpoints():
    """Test HTTP endpoints"""
    print("\n🌐 Testing HTTP endpoints...")
    
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/",
        "/health",
        "/api/quick-status"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
                if endpoint == "/":
                    data = response.json()
                    print(f"   - Simulation running: {data.get('simulation', {}).get('running', False)}")
                    print(f"   - Satellites: {data.get('simulation', {}).get('satellites', 0)}")
                    print(f"   - Debris: {data.get('simulation', {}).get('debris', 0)}")
                    print(f"   - Threats: {data.get('simulation', {}).get('threats', 0)}")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    return True

def test_maneuver_execution():
    """Test maneuver execution"""
    print("\n🚀 Testing maneuver execution...")
    
    try:
        # First get system status to find a satellite
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code != 200:
            print("❌ Cannot get system status")
            return False
        
        # Try to execute a maneuver for the first satellite
        satellite_id = "SAT-001"  # Known from simple_simulation_engine
        
        response = requests.post(f"http://localhost:8000/api/maneuver/execute/{satellite_id}", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Maneuver execution: {result.get('status')}")
            print(f"   - Message: {result.get('message')}")
        else:
            print(f"❌ Maneuver execution failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Maneuver test failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🧪 ACM System Full Test Suite")
    print("=" * 50)
    
    # Test HTTP endpoints first
    test_http_endpoints()
    
    # Test WebSocket
    await test_websocket()
    
    # Test maneuver execution
    test_maneuver_execution()
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("\nIf all tests passed, the system is ready for demo!")

if __name__ == "__main__":
    asyncio.run(main())