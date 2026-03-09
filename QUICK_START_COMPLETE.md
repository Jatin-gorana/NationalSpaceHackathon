# ACM System - Complete Quick Start Guide

## 🚀 Start the System (2 Commands)

### Terminal 1: Backend
```bash
cd acm-system/backend
python main.py
```

**Expected Output**:
```
🛰️  Generating initial constellation...
✅ Generated 50 satellites
✅ Generated 500 debris objects
⚠️  Created 5 collision scenarios for testing
🚀 Starting simulation loop (20 Hz)...
📡 WebSocket broadcast started (20 Hz)
✅ Simulation engine started
```

### Terminal 2: Frontend
```bash
cd acm-system/frontend
npm run dev
```

**Expected Output**:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

## 🎯 Access the Dashboard

Open browser: **http://localhost:5173**

You should see:
- 🌍 Blue Earth in center
- 🟢 Green satellites orbiting
- 🟠 Orange debris particles
- 💙 Cyan orbit prediction lines
- ⚡ "LIVE 20Hz" badge (top right)

## 🎮 How to Use

### 1. Watch Real-Time Simulation
- Satellites orbit Earth continuously
- Frame counter increments (top header)
- Positions update 20 times per second
- Smooth, realistic motion

### 2. Wait for Collision Risks (10-60 seconds)
- Left panel "Collision Alerts" shows threats
- Satellites turn RED when at risk
- Threat counter increases
- Critical/Warning alerts appear

### 3. Trigger AI Auto-Resolve
1. Click **"🤖 AI Auto-Resolve"** button (left panel)
2. Watch satellites change orbit in real-time
3. Red satellites turn green
4. Success message: "✅ Resolved X collision risks"
5. Threat counter drops to 0

### 4. Monitor System
- **Fuel Panel**: Shows fuel consumption
- **Maneuver Timeline**: Lists scheduled maneuvers
- **System Status**: Overall health metrics
- **3D View**: Visual confirmation of safe orbits

## 🎨 3D View Controls

- **🖱️ Left Click + Drag**: Rotate camera
- **🖱️ Right Click + Drag**: Pan camera
- **🖱️ Scroll Wheel**: Zoom in/out
- **Double Click**: Reset view

## 📊 Dashboard Panels

### Left Side
1. **Collision Alerts**
   - Total threats
   - Critical/Warning counts
   - AI Auto-Resolve button
   - Individual collision details

2. **Fuel Status**
   - Fleet average fuel
   - Individual satellite fuel levels
   - Color-coded bars (green/yellow/red)

### Center
3. **3D Visualization**
   - Real-time satellite positions
   - Debris field
   - Orbit prediction lines
   - Earth with rotation
   - Legend and controls

### Right Side
4. **Maneuver Timeline**
   - Scheduled maneuvers
   - Execution status
   - Delta-v values
   - Fuel costs

## 🔧 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Get Current State
```bash
curl http://localhost:8000/
```

### Auto-Resolve Collisions
```bash
curl -X POST http://localhost:8000/api/ai/auto-resolve
```

### Optimize Entire Fleet
```bash
curl -X POST http://localhost:8000/api/ai/optimize-fleet
```

### Get Telemetry
```bash
curl http://localhost:8000/api/telemetry/satellites
curl http://localhost:8000/api/telemetry/debris
```

## 🎯 Key Features Demonstrated

### 1. Real-Time Physics Simulation
- RK4 orbital propagation
- 20 Hz update rate
- Accurate gravitational dynamics
- Earth-Centered Inertial (ECI) coordinates

### 2. Collision Detection
- KDTree spatial indexing
- 10 km search radius
- 100m critical threshold
- Real-time threat assessment

### 3. AI-Powered Optimization
- Automatic collision avoidance
- Perpendicular velocity maneuvers
- Fuel-efficient trajectory changes
- One-click resolution

### 4. 3D Visualization
- Three.js rendering
- Real-time position updates
- Orbit prediction lines
- Interactive camera controls

### 5. WebSocket Streaming
- 20 Hz data broadcast
- Low-latency updates
- Automatic reconnection
- Efficient data transfer

## 📈 Performance Expectations

- **Frame Rate**: 60 FPS
- **Update Rate**: 20 Hz (50ms intervals)
- **Latency**: < 100ms
- **Satellites**: 50 tracked
- **Debris**: 500 total (100 visible)
- **Memory**: ~200 MB
- **CPU**: ~10-20% (single core)

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Install dependencies
pip install -r requirements.txt

# Check Python version (3.8+)
python --version
```

### Frontend Won't Start
```bash
# Install dependencies
npm install

# Clear cache
rm -rf node_modules package-lock.json
npm install
```

### No Satellites Visible
1. Check WebSocket connection (LIVE 20Hz badge)
2. Open browser console (F12)
3. Look for errors
4. Refresh page
5. Restart backend

### Auto-Resolve Not Working
1. Wait for collision risks to appear (10-60 seconds)
2. Check threat counter > 0
3. Verify backend is running
4. Check browser console for errors

## 🎓 Understanding the System

### Coordinate System
- **Backend**: ECI coordinates (km)
- **Frontend**: Three.js units (scaled 1:500)
- **Earth Radius**: 6371 km → 12.74 units
- **Satellite Altitude**: 400-2000 km → 13.5-16.7 units

### Collision Scenarios
- 5 debris objects on collision course
- Positioned 0.5 seconds ahead of satellites
- Velocity 1% faster (catching up)
- Collision within 1-5 minutes if not resolved

### Maneuver Mechanics
- **Direction**: Perpendicular to velocity
- **Magnitude**: 50 m/s (0.05 km/s)
- **Effect**: Changes orbital plane
- **Fuel Cost**: 5% per maneuver
- **Result**: Avoids debris path

## 📚 Documentation

- **README.md**: Project overview
- **API_DOCUMENTATION.md**: Complete API reference
- **PHYSICS_REFERENCE.md**: Orbital mechanics details
- **AI_OPTIMIZATION.md**: Genetic algorithm explanation
- **ANIMATION_AND_AI_GUIDE.md**: This feature guide
- **VISUALIZATION_DEBUG.md**: Troubleshooting visualization

## 🎉 Success Indicators

You know it's working when:
- ✅ Satellites orbit Earth smoothly
- ✅ Frame counter increments continuously
- ✅ "LIVE 20Hz" badge shows green
- ✅ Collision alerts appear after 10-60 seconds
- ✅ Red satellites turn green after auto-resolve
- ✅ Threat counter drops to 0
- ✅ Fuel levels decrease slightly
- ✅ No errors in browser console

## 🚀 Next Steps

1. **Experiment**: Try different camera angles
2. **Monitor**: Watch collision scenarios develop
3. **Resolve**: Use AI auto-resolve multiple times
4. **Explore**: Check API endpoints
5. **Customize**: Modify parameters in code
6. **Extend**: Add new features

## 💡 Pro Tips

- Zoom out to see full constellation
- Watch orbit lines to predict paths
- Monitor fuel levels before resolving
- Use browser DevTools to inspect data
- Check backend console for detailed logs
- Refresh page to reset simulation

---

**System Status**: ✅ Fully Operational

**Features**: Real-time simulation • AI optimization • 3D visualization • WebSocket streaming

**Ready to launch!** 🚀
