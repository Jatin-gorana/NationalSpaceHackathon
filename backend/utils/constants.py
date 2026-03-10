"""Physical and system constants for orbital mechanics"""

# Gravitational parameter for Earth (km^3/s^2)
MU_EARTH = 398600.4418

# Collision detection threshold (km)
COLLISION_THRESHOLD = 0.1  # 100 meters

# Spatial search radius for KDTree (km)
SPATIAL_SEARCH_RADIUS = 50.0

# Orbital slot tolerance (km)
SLOT_TOLERANCE = 10.0

# Prediction horizon (hours)
PREDICTION_HORIZON = 24

# Time step for propagation (seconds)
TIME_STEP = 10  # High-precision 10-second timestep

# Earth radius (km)
EARTH_RADIUS = 6371.0

# Fuel thresholds
LOW_FUEL_THRESHOLD = 5.0  # Percentage
CRITICAL_FUEL_THRESHOLD = 10.0  # Percentage

# Graveyard orbit altitude (km above LEO)
GRAVEYARD_ALTITUDE = 2500.0

# Thruster cooldown (seconds)
THRUSTER_COOLDOWN = 3600.0

# Communication delay (seconds)
COMMUNICATION_DELAY = 10.0

# Maneuver execution tolerance (seconds)
MANEUVER_EXECUTION_TOLERANCE = 5.0
