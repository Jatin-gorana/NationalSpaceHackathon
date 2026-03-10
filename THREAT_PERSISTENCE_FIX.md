# ✅ Threat Persistence Logic Fixed

## Problem

The threat debris was being created but immediately removed because:
1. Threat debris was created too far away (±10km radius, ±0.1 radians angle)
2. Distance calculation showed it wasn't within 100km threshold
3. Debris was removed immediately without ever showing as a threat
4. Satellite never turned red

## Solution

### 1. **Create Threat Debris Much Closer**

**Before**:
```python
radius=target_sat.radius + np.random.uniform(-10, 10)      # ±10 km
angle=target_sat.angle + np.random.uniform(-0.1, 0.1)      # ±0.1 radians
angular_velocity += np.random.uniform(-0.0001, 0.0001)     # Different speed
```

**After**:
```python
radius=target_sat.radius + np.random.uniform(-5, 5)        # ±5 km (closer)
angle=target_sat.angle + np.random.uniform(-0.05, 0.05)    # ±0.05 radians (closer)
angular_velocity += np.random.uniform(-0.00005, 0.00005)   # Nearly same speed
```

**Result**: Debris stays within 100km threshold and triggers collision detection

### 2. **Removed Auto-Cleanup Logic**

**Removed**:
```python
# This was removing threats too early
debris_to_remove = []
for idx, debris in enumerate(self.debris):
    if "THREAT" in debris.id and idx not in active_threats:
        debris_to_remove.append(idx)
```

**Why**: Threats should persist until user manually resolves them with auto-resolve button

### 3. **Manual Threat Removal on Maneuver**

**Added to apply_maneuver()**:
```python
# Remove threat debris that was threatening this satellite
debris_to_remove = []
sat_pos = np.array(satellite.get_position())
for idx, debris in enumerate(self.debris):
    if "THREAT" in debris.id:
        deb_pos = np.array(debris.get_position())
        distance = np.linalg.norm(sat_pos - deb_pos)
        if distance < 150.0:  # Remove threats within 150km
            debris_to_remove.append(idx)

# Remove in reverse order
for idx in sorted(debris_to_remove, reverse=True):
    removed = self.debris.pop(idx)
    print(f"🗑️ Threat debris removed by maneuver: {removed.id}")
```

**Result**: Threats are only removed when user clicks auto-resolve button

## Expected Behavior Now

### Timeline:

```
0s:     System starts
60-120s: ⚠️ COLLISION THREAT CREATED: THREAT-001 near SAT-005
        🔴 SAT-005 turns RED
        🔴 Red warning line appears
        📈 Threat counter = 1

180s:   User clicks "AUTO-RESOLVE ALL THREATS"
        ✅ Maneuver executed for SAT-005
        🗑️ Threat debris removed by maneuver: THREAT-001
        🟢 SAT-005 turns GREEN
        📉 Threat counter = 0

240-300s: ⚠️ COLLISION THREAT CREATED: THREAT-002 near SAT-012
        🔴 SAT-012 turns RED
        (cycle repeats)
```

## Key Changes

| Aspect | Before | After |
|--------|--------|-------|
| Threat creation distance | ±10km radius | ±5km radius |
| Threat angle offset | ±0.1 radians | ±0.05 radians |
| Threat persistence | Auto-removed | Persists until maneuver |
| Removal trigger | Distance check | User action (auto-resolve) |
| Satellite visibility | Never turned red | Turns red and stays red |

## Verification

### Backend Logs Should Show:

```
⚠️ COLLISION THREAT CREATED: THREAT-001 near SAT-005
🔄 Simulation tick: 120.0s, Threats: 1, Debris: 11
🔄 Simulation tick: 125.0s, Threats: 1, Debris: 11
✅ Maneuver executed for SAT-005: new radius 7060.0 km, fuel 95.0%
🗑️ Threat debris removed by maneuver: THREAT-001
🔄 Simulation tick: 130.0s, Threats: 0, Debris: 10
```

### Frontend Should Show:

1. ✅ Satellite turns RED when threat appears
2. ✅ Red warning line appears
3. ✅ Threat counter increases
4. ✅ Collision alert shows in left panel
5. ✅ Auto-resolve button becomes active
6. ✅ After clicking auto-resolve:
   - Satellite turns GREEN
   - Red warning line disappears
   - Threat counter resets to 0

## Result

✅ **Threats now persist until manually resolved**
✅ **Satellites turn red and stay red**
✅ **Red warning lines visible**
✅ **Only removed when user clicks auto-resolve**
✅ **Continuous threat generation every 1-2 minutes**
✅ **Demo works as intended**