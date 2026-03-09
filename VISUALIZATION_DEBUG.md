# Visualization Debugging Guide

## Changes Made

### 1. Fixed Coordinate System
- **Issue**: Y and Z coordinates were swapped in the visualization
- **Fix**: Changed from `[x, z, y]` to `[x, y, z]` mapping
- **Files**: `SatelliteViewer.jsx` - Satellite, Debris, and OrbitLine components

### 2. Enhanced Satellite Visibility
- Increased satellite mesh size from 0.15 to 0.3 units
- Increased emissive intensity from 0.5 to 0.8
- Made solar panels more visible with emissive materials
- Added debug logging for SAT-001 position

### 3. Improved Debris Rendering
- Fixed debris size to 0.08 units (more visible)
- Increased emissive intensity from 0.3 to 0.5
- Simplified position calculation

### 4. Added Test Satellite
- Yellow test cube at position [14, 0, 0]
- Should be visible next to Earth
- Helps verify rendering pipeline works

### 5. Added Debug Logging
- Console logs when satellites are received
- Position logging for first satellite (SAT-001)
- Distance from origin calculation

## Testing Steps

### 1. Start Backend
```bash
cd acm-system/backend
python main.py
```

Expected output:
```
🛰️  Generating initial constellation...
✅ Generated 50 satellites
✅ Generated 500 debris objects
🚀 Starting simulation loop (20 Hz)...
📡 WebSocket broadcast started (20 Hz)
```

### 2. Test WebSocket Connection
Open `acm-system/test_websocket.html` in browser
- Should show "Connected ✅"
- Should log satellite positions every 50ms
- Verify positions are ~7000 km from origin

### 3. Start Frontend
```bash
cd acm-system/frontend
npm run dev
```

### 4. Open Browser Console
Check for:
- ✅ WebSocket connected message
- 📊 Received satellites count
- SAT-001 position logs
- No WebGL errors

### 5. Visual Checks
- [ ] Earth sphere visible at center (blue, radius ~12.7 units)
- [ ] Yellow test satellite visible next to Earth
- [ ] Green satellites orbiting Earth
- [ ] Orange debris particles
- [ ] Cyan orbit lines
- [ ] Stars in background
- [ ] Can rotate/zoom camera

## Expected Positions

### Earth
- Position: [0, 0, 0]
- Radius: 6371 km = 12.74 units (scaled)

### Satellites
- Orbital radius: 6771-8371 km (400-2000 km altitude)
- Scaled: 13.5-16.7 units from origin
- Should be visible around Earth

### Test Satellite
- Position: [14, 0, 0] units
- Should appear as yellow cube next to Earth

## Common Issues

### Issue: Nothing visible except Earth
**Cause**: Satellites might be behind camera or outside frustum
**Fix**: 
- Check console for position logs
- Try zooming out (scroll wheel)
- Rotate camera (left mouse drag)

### Issue: WebSocket not connecting
**Cause**: Backend not running or wrong port
**Fix**:
- Verify backend is running on port 8000
- Check `http://localhost:8000/health`
- Look for CORS errors in console

### Issue: Satellites not moving
**Cause**: WebSocket not receiving updates
**Fix**:
- Check "LIVE 20Hz" badge in header
- Verify frame counter is incrementing
- Check backend console for broadcast messages

### Issue: Performance problems
**Cause**: Too many objects rendering
**Fix**:
- Debris limited to 100 closest objects
- Orbit lines use 80 segments max
- Consider reducing satellite count in backend

## Coordinate System

### Backend (ECI - Earth-Centered Inertial)
- X: Points to vernal equinox
- Y: 90° from X in equatorial plane
- Z: North pole
- Units: kilometers

### Frontend (Three.js)
- X: Right
- Y: Up
- Z: Out of screen (toward viewer)
- Units: arbitrary (scaled by 1/500)

### Scaling
```
VISUAL_SCALE = 1/500
Three.js units = km * VISUAL_SCALE
```

Example:
- 7000 km → 14 units
- 6371 km (Earth) → 12.74 units

## Camera Configuration
```javascript
position: [0, 0, 25]  // 25 units from origin
fov: 60
near: 0.1
far: 1000
```

This should capture objects at 13-17 units from origin.

## Next Steps if Still Not Visible

1. **Verify data is arriving**:
   ```javascript
   console.log('Satellites:', satellites.length)
   console.log('First sat:', satellites[0])
   ```

2. **Check if test satellite is visible**:
   - Yellow cube at [14, 0, 0]
   - If not visible, camera/rendering issue

3. **Simplify scene**:
   - Comment out orbit lines
   - Comment out debris
   - Render only satellites

4. **Check Three.js version**:
   - Ensure @react-three/fiber and three are compatible
   - Try updating packages

5. **Use React DevTools**:
   - Inspect SatelliteViewer props
   - Verify satellites array has data
   - Check if components are mounting

## Performance Metrics

Target: 60 FPS with:
- 50 satellites (with orbit lines)
- 100 debris (limited from 500)
- Real-time updates at 20 Hz

Monitor in browser:
- Press F12 → Performance tab
- Record for 5 seconds
- Check frame rate
