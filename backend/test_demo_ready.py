#!/usr/bin/env python3
"""Test script to verify demo readiness"""

import asyncio
import json
import websockets
import requests
import time

async def test_websocket():
    """Test WebSocket connection and data flow"""
    print("🧪 Testing WebSocket connection...")
    
    try:
        uri = "ws://localhost:8000/ws/simulation"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully")
            
            # Receive initial data
            data = await websocket.recv()
            parsed = json.loads(data)
            
            print(f"📡 Received data: {len(parsed.get('satellites', []))} satellites, {len(parsed.get('debris', []))} debris")
            print(f"🚨 Threats: {parsed.get('threats', 0)}")
            
            # Test ping/pong
            await websocket.send("ping")
            response = await websocket.recv()
            if response == "pong":
                print("🏓 Ping/pong working")
            
            return True
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

def test_http_endpoints():
    """Test HTTP endpoints"""
    print("🧪 Testing HTTP endpoints...")
    
    endpoints = [
        ("Health", "http://localhost:8000/health"),
        ("Root", "http://localhost:8000/"),
        ("Quick Status", "http://localhost:8000/api/quick-status"),
        ("Force Collisions", "http://localhost:8000/debug/force-collisions")
    ]
    
    success = 0
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
                success += 1
            else:
                print(f"❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    return success == len(endpoints)

def test_maneuver_execution():
    """Test maneuver execution"""
    print("🧪 Testing maneuver execution...")
    
    try:
        # Execute maneuver for SAT-001
        response = requests.post("http://localhost:8000/api/maneuver/execute/SAT-001", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Maneuver execution: {result.get('status')}")
            return True
        else:
            print(f"❌ Maneuver execution failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Maneuver test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Demo Readiness Test")
    print("=" * 40)
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    for i in range(10):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready")
                break
        except:
            pass
        
        if i == 9:
            print("❌ Backend not responding after 10 attempts")
            return False
        
        time.sleep(1)
    
    # Run tests
    tests = [
        ("HTTP Endpoints", test_http_endpoints),
        ("Maneuver Execution", test_maneuver_execution),
        ("WebSocket Connection", test_websocket)
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n🧪 Running {name} test...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {name}: PASSED")
            else:
                print(f"❌ {name}: FAILED")
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
    
    print("\n" + "=" * 40)
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 DEMO READY! All systems operational.")
        print("\nNext steps:")
        print("1. Start frontend: cd frontend && npm run dev")
        print("2. Open browser: http://localhost:5173")
        print("3. Verify smooth animation and WebSocket connection")
        return True
    else:
        print("❌ Demo not ready. Fix failing tests above.")
        return False

if __name__ == "__main__":
    asyncio.run(main())