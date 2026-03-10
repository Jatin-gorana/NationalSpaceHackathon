# 🔧 Threat Generation Logic Fix

## Problem Identified

After resolving a threat with the auto-resolve button, no new threats appeared for 5-10 minutes. This was caused by:

1. **Old threat debris persisting**: When a maneuver was executed, the satellite moved to a new orbit (radius +60km), but the threat debris stayed in the old orbit
2. **No collision detection**: The debris was no longer close to any satellite, so no new threats were detected
3. **Threat generation still running**: But the old debris was blocking the system from creating meaningful new threats

## Solution Implemented

### 1. **Automatic Cleanup of Inactive Threats**

```python
# Track which debris are still threats
active_threats = set()

# After collision detection, remove old threat debris
debris_to_remove = []
for idx, debris in enumerate(self.debris):
    if "THREAT" in debris.id and idx not in active_threats:
        debris_to_remove.append(idx)

# Remove in reverse order
for idx in sorted(debris_to_remove, reverse=True):
    removed = self.debris.pop(idx)
    print(f"🗑️ Removed inactive threat debris: {removed.id}")
```

**What this does**:
- Identifies threat debris (those with "THREAT" in the name)
- Removes them if they're no longer threatening any satellite
- Keeps background debris (regular orbital debris)

### 2. **Maintain Minimum Background Debris**

```python
# Ensure we always have at least 10 background debris
while len(self.debris) < 10:
    debris = SimpleDebris(f"DEB-{len(self.debris)+1:03d}", ...)
    self.debris.append(debris)
```

**What this does**:
- Ensures the system always has at least 10 background debris objects
- Automatically creates new ones if they fall below the minimum
- Maintains visual density in the 3D view

### 3. **Faster Threat Generation**

```python
# Changed from 120-180 seconds to 60-120 seconds
self.threat_generation_interval = np.random.uniform(60, 120)  # 1-2 minutes
```

**What this does**:
- Threats now appear every 1-2 minutes instead of 2-3 minutes
- Faster demo pacing for judges
- More frequent collision scenarios

## How It Works Now

### Timeline After Fix:

```
0s:     System starts
60-120s: First threat appears (random satellite turns red)
180s:   User clicks auto-resolve (satellite turns green)
        Old threat debris is removed
        Background debris count restored to 10
240-300s: Second threat appears (different satellite turns red)
360s:   Third threat appears
...
```

### Debris Management:

**Before Fix**:
- Threat debris: Created, never removed
- Background debris: 10 initial
- Total debris: Grows indefinitely
- Result: Old threats block new ones

**After Fix**:
- Threat debris: Created, removed when no longer threatening
- Background debris: Maintained at minimum 10
- Total debris: Stays manageable (10-15)
- Result: Continuous threat generation

## Code Changes

### File: `backend/services/simple_simulation_engine.py`

**Change 1**: Threat generation interval
```python
# OLD: np.random.uniform(120, 180)  # 2-3 minutes
# NEW: np.random.uniform(60, 120)   # 1-2 minutes
```

**Change 2**: Collision detection with cleanup
```python
# Added:
- active_threats tracking
- Debris removal logic
- Background debris restoration
```

## Testing the Fix

### Expected Behavior:

1. **First threat** (60-120s): Satellite turns red
2. **Auto-resolve**: Satellite turns green, threat debris removed
3. **Second threat** (60-120s later): New satellite turns red
4. **Continuous cycle**: Threats appear every 1-2 minutes indefinitely

### Verification:

Check backend logs for:
```
⚠️ COLLISION THREAT CREATED: THREAT-001 near SAT-005
🗑️ Removed inactive threat debris: THREAT-001
➕ Added background debris: DEB-011
⚠️ COLLISION THREAT CREATED: THREAT-002 near SAT-012
```

## Result

✅ **Threats now appear continuously every 1-2 minutes**
✅ **Old threat debris is automatically cleaned up**
✅ **Background debris count maintained**
✅ **Demo runs smoothly indefinitely**
✅ **Judges see continuous collision scenarios**

The system now behaves like a real satellite constellation management system with continuous threat generation and automatic resolution.