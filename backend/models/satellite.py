from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class Satellite(BaseModel):
    object_id: str
    position: List[float] = Field(..., min_length=3, max_length=3, description="Position [x, y, z] in km")
    velocity: List[float] = Field(..., min_length=3, max_length=3, description="Velocity [vx, vy, vz] in km/s")
    timestamp: datetime
    assigned_slot: List[float] = Field(default=[0, 0, 0], description="Assigned orbital slot [x, y, z] in km")
    fuel_remaining: float = Field(default=100.0, ge=0, le=100, description="Fuel percentage")
    status: str = Field(default="operational", description="operational | maneuvering | critical | graveyard | decommissioned")
    last_maneuver_time: float = Field(default=0.0, description="Timestamp of last maneuver execution (seconds)")
    scheduled_maneuvers: List[dict] = Field(default_factory=list, description="List of scheduled maneuvers")
    in_recovery: bool = Field(default=False, description="Whether satellite is recovering to assigned slot")
    
    class Config:
        json_schema_extra = {
            "example": {
                "object_id": "SAT-001",
                "position": [7000.0, 0.0, 0.0],
                "velocity": [0.0, 7.5, 0.0],
                "timestamp": "2026-03-09T12:00:00Z",
                "assigned_slot": [7000.0, 0.0, 0.0],
                "fuel_remaining": 85.5,
                "status": "operational"
            }
        }
