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
