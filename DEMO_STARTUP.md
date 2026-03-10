# 🚀 DEMO STARTUP GUIDE

## Quick Demo Setup (2 minutes)

### Terminal 1 - Backend
```bash
cd acm-system/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
🚀 Starting simple simulation engine...
🛰️ Initializing simple constellation...
✅ Created 20 satellites and 100 debris
✅ Simple simulation engine started
📡 WebSocket broadcast started (20 Hz)
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 - Frontend
```bash
cd acm-system/frontend
npm run dev
```

**Expected Output:**
```
Local:   http://localhost:5173/
Network: http://192.168.x.x:5173/
```

### Open Browser
Navigate to: `http://localhost:5173`

## Expected Demo Behavior

### 1. Instant Connection (0-5 seconds)
- ✅ WebSocket connects immediately
- ✅ "LIVE 20Hz" badge shows green
- ✅ Dashboard loads with data

### 2. Continuous Animation (ongoing)
- 🌍 Earth rotates slowly
- 🛰️ Satellites orbit smoothly around Earth
- 🔴 Debris particles move independently
- 📊 Frame counter increments continuously

### 3. Collision Scenarios (10-30 seconds)
- ⚠️ 3-5 satellites turn RED (at risk)
- 🔴 Red warning lines appear
- 📈 Threat counter increases
- 🚨 Collision alerts show in left panel

### 4. Manual Intervention (user action)
- 🎯 Click "🤖 AUTO-RESOLVE ALL THREATS"
- ⚡ Maneuvers execute immediately
- ✅ Red satellites turn GREEN
- 📉 Threat counter drops to 0

### 5. Continuous Operation
- 🔄 New threats may develop over time
- 🛰️ Satellites continue orbiting
- 📡 Real-time updates at 20 Hz

## Debug Commands

### Check Backend Health
```bash
curl http://localhost:8000/health
```

### Test WebSocket
```bash
# Open debug page
open acm-system/debug_websocket.html
```

### Force Collision Detection
```bash
curl http://localhost:8000/debug/force-collisions
```

## Troubleshooting

### Backend Won't Start
```bash
# Check Python version
python --version  # Need 3.11+

# Install dependencies
pip install -r requirements.txt
```

### Frontend Won't Connect
- Check backend is running on port 8000
- Check browser console for WebSocket errors
- Try refreshing the page

### No Animation
- Check browser console for Three.js errors
- Verify WebGL is enabled
- Check frame counter is incrementing

## Demo Script (5 minutes)

**Minute 1**: Show system startup and constellation
**Minute 2**: Point out smooth orbital motion and Earth rotation
**Minute 3**: Highlight collision detection (red satellites)
**Minute 4**: Demonstrate auto-resolve functionality
**Minute 5**: Show continuous operation and real-time updates

## Success Criteria

✅ WebSocket connects in < 5 seconds
✅ Satellites orbit smoothly (visible movement)
✅ Earth rotates continuously
✅ Collision threats appear (red satellites)
✅ Auto-resolve works (red → green)
✅ 20 Hz updates (frame counter)
✅ No console errors

**Status**: 🚀 READY FOR DEMO