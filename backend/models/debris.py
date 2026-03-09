from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class Debris(BaseModel):
    object_id: str
    position: List[float] = Field(..., min_length=3, max_length=3, description="Position [x, y, z] in km")
    velocity: List[float] = Field(..., min_length=3, max_length=3, description="Velocity [vx, vy, vz] in km/s")
    timestamp: datetime
    size_estimate: float = Field(default=1.0, ge=0, description="Estimated size in meters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "object_id": "DEB-12345",
                "position": [7100.0, 500.0, 200.0],
                "velocity": [0.5, 7.3, 0.2],
                "timestamp": "2026-03-09T12:00:00Z",
                "size_estimate": 0.5
            }
        }
