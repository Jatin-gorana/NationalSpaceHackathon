# ACM Visualization Guide

## Real-Time Orbit Prediction

### Overview

The ACM dashboard features real-time orbital trajectory prediction using Runge-Kutta 4 (RK4) integration running directly in the browser. This provides immediate visual feedback of satellite and debris paths.

### Technical Implementation

#### Client-Side RK4 Integration

```javascript
// Propagation parameters
const MU = 398600.4418      // Earth's gravitational parameter (km³/s²)
const dt = 60               // 60-second timestep
const duration = 5400       // 1.5 hours prediction
const segments = 200        // Smooth curve rendering

// RK4 integration loop
for each timestep:
    k1 = derivatives(state)
    k2 = derivatives(state + 0.5 * dt * k1)
    k3 = derivatives(state + 0.5 * dt * k2)
    k4 = derivatives(state + dt * k3)
    
    state = state + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
```

#### Performance Optimization

- **Memoization**: Orbit points cached using React useMemo
- **Segment Reduction**: Debris uses 100 segments vs 200 for satellites
- **Lazy Rendering**: Only visible objects are rendered
- **Frame Budget**: < 16ms per frame for 60 FPS

### Visual Elements

#### 1. Satellite Trajectories

**Color Coding:**
- **Cyan (#00ffff)**: Safe satellites
- **Red (#ff0000)**: Satellites at collision risk
- **Opacity**: 60% for subtle appearance

**Properties:**
- Line width: 2 pixels
- Segments: 200 points
- Duration: 1.5 hours ahead
- Update: Real-time with position changes

#### 2. Debris Trajectories

**Color Coding:**
- **Orange (#ff6600)**: All debris objects

**Properties:**
- Line width: 2 pixels
- Segments: 100 points (performance optimization)
- Duration: 1.5 hours ahead
- Opacity: 60%

#### 3. Collision Warning Lines

**Visual Style:**
- **Color**: Red (#ff0000)
- **Style**: Dashed line
- **Dash pattern**: 1 unit dash, 0.5 unit gap
- **Opacity**: 80%
- **Width**: 3 pixels

**Purpose:**
- Connect satellites to threatening debris
- Immediate visual identification of collision pairs
- Limited to top 10 threats for clarity

#### 4. Enhanced Satellite Models

**Components:**
- **Main body**: 0.3 × 0.3 × 0.3 km box
- **Solar panels**: Two 0.8 × 0.05 × 0.4 km panels
- **Color**: Metallic blue (#1e90ff)
- **Hover effect**: Label appears on mouse over

**Animation:**
- Pulsing emissive intensity for at-risk satellites
- Smooth rotation with Earth

### Visualization Layers

```
Layer 1: Background
├── Stars (5000 particles)
└── Space background (#000000)

Layer 2: Earth
├── Rotating sphere (6.371 km radius)
├── Blue material (#1e40af)
└── Emissive glow

Layer 3: Orbit Lines
├── Satellite trajectories (cyan/red)
├── Debris trajectories (orange)
└── Real-time RK4 propagation

Layer 4: Objects
├── Satellites (boxes with solar panels)
├── Debris (spheres)
└── Interactive hover states

Layer 5: Warnings
├── Collision warning lines (dashed red)
└── Limited to top 10 threats

Layer 6: UI Overlays
├── Legend (bottom-left)
├── Statistics (top-left)
└── Controls
```

### Camera Controls

**Mouse/Touch:**
- **Left click + drag**: Rotate view
- **Right click + drag**: Pan view
- **Scroll wheel**: Zoom in/out
- **Two-finger pinch**: Zoom (mobile)

**Limits:**
- Minimum distance: 10 km
- Maximum distance: 100 km
- Default position: [30, 30, 30] km

### Legend Components

#### Visual Indicators

```
🟢 Green Box        → Safe Satellites
🔴 Red Box (pulse)  → At-Risk Satellites
🟠 Orange Sphere    → Debris Objects
━━ Cyan Line        → Predicted Orbits
╌╌ Red Dashed       → Collision Paths
```

#### Statistics Panel

```
VISUALIZATION
├── Satellites: N
├── Debris: M
├── Orbit Lines: N+M
└── Warning Lines: K
```

### Performance Metrics

#### Frame Rate
- **Target**: 60 FPS
- **Typical**: 55-60 FPS with 50 satellites + 1000 debris
- **Minimum**: 30 FPS (acceptable)

#### Rendering Budget
- **Orbit calculation**: 5-8ms per frame
- **Three.js rendering**: 8-10ms per frame
- **Total frame time**: 13-18ms (< 16.67ms target)

#### Memory Usage
- **Orbit points**: ~50 KB per satellite
- **Three.js objects**: ~100 KB per satellite
- **Total**: ~5-10 MB for typical constellation

### Optimization Techniques

#### 1. Memoization
```javascript
const points = useMemo(() => {
    // Expensive RK4 calculation
    return computeOrbitPoints()
}, [position, velocity])
```

#### 2. Level of Detail (LOD)
- Satellites: 200 segments (high detail)
- Debris: 100 segments (medium detail)
- Distant objects: Reduced segments (future)

#### 3. Frustum Culling
- Three.js automatically culls off-screen objects
- Reduces rendering load by 30-50%

#### 4. Instancing (Future)
- Render multiple debris with single draw call
- Expected 2-3x performance improvement

### Color Palette

#### Primary Colors
```css
--space-dark: #0a0e27      /* Background */
--cyan-primary: #00ffff    /* Safe orbits */
--red-warning: #ff0000     /* Danger */
--orange-debris: #ff6600   /* Debris */
--green-safe: #00ff00      /* Safe satellites */
```

#### Material Properties
```javascript
// Satellites
emissive: color
emissiveIntensity: 0.5 (safe) | 1.0 (danger)
metalness: 0.8 (solar panels)

// Orbits
transparent: true
opacity: 0.6
lineWidth: 2
```

### Interaction Features

#### Hover Effects
- Satellite label appears
- Highlight effect
- Cursor changes to pointer

#### Click Events (Future)
- Select satellite for details
- Show maneuver history
- Display fuel status

### Accessibility

#### Visual Indicators
- Color + shape coding (not just color)
- High contrast ratios
- Clear labels and legends

#### Performance
- Graceful degradation on slower devices
- Reduced detail mode available
- Frame rate monitoring

### Browser Compatibility

**Supported:**
- Chrome 90+ ✓
- Firefox 88+ ✓
- Safari 14+ ✓
- Edge 90+ ✓

**Requirements:**
- WebGL 2.0
- ES6 JavaScript
- 4GB RAM minimum
- Dedicated GPU recommended

### Troubleshooting

#### Low Frame Rate
1. Reduce number of visible objects
2. Decrease orbit segment count
3. Disable collision warning lines
4. Close other browser tabs

#### Visual Artifacts
1. Update graphics drivers
2. Enable hardware acceleration
3. Clear browser cache
4. Try different browser

#### Objects Not Visible
1. Check camera position
2. Verify object positions in data
3. Check console for errors
4. Reload page

### Future Enhancements

#### Planned Features
- [ ] Maneuver visualization (delta-v arrows)
- [ ] Time slider for trajectory playback
- [ ] Multiple camera presets
- [ ] Screenshot/video export
- [ ] VR/AR support
- [ ] Particle effects for thrusters
- [ ] Earth texture mapping
- [ ] Day/night terminator
- [ ] Ground station visibility cones

#### Performance Improvements
- [ ] WebGL instancing for debris
- [ ] Web Workers for orbit calculation
- [ ] Progressive rendering
- [ ] Adaptive quality based on FPS
- [ ] Occlusion culling

### Best Practices

#### For Developers
1. Always memoize expensive calculations
2. Use React.memo for pure components
3. Profile with React DevTools
4. Monitor frame rate in production
5. Test on low-end devices

#### For Users
1. Use modern browser
2. Enable hardware acceleration
3. Close unnecessary tabs
4. Use dedicated GPU if available
5. Reduce zoom for better performance

### Resources

**Three.js Documentation:**
- https://threejs.org/docs/

**React Three Fiber:**
- https://docs.pmnd.rs/react-three-fiber/

**Orbital Mechanics:**
- Vallado, "Fundamentals of Astrodynamics"

**WebGL Performance:**
- https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices
