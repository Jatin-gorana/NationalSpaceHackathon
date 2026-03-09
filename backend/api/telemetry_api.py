"""Telemetry ingestion API endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime
from models.satellite import Satellite
from models.debris import Debris
from services.telemetry_service import telemetry_service

router = APIRouter()

class TelemetryInput(BaseModel):
    object_id: str
    type: Literal["satellite", "debris"]
    position: List[float] = Field(..., min_length=3, max_length=3)
    velocity: List[float] = Field(..., min_length=3, max_length=3)
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "object_id": "SAT-001",
                "type": "satellite",
                "position": [7000.0, 0.0, 0.0],
                "velocity": [0.0, 7.5, 0.0],
                "timestamp": "2026-03-09T12:00:00Z"
            }
        }

@router.post("/telemetry")
async def ingest_telemetry(data: TelemetryInput):
    """
    Ingest telemetry data for satellites or debris
    """
    try:
        if data.type == "satellite":
            satellite = Satellite(
                object_id=data.object_id,
                position=data.position,
                velocity=data.velocity,
                timestamp=data.timestamp
            )
            telemetry_service.update_satellite(satellite)
        else:
            debris = Debris(
                object_id=data.object_id,
                position=data.position,
                velocity=data.velocity,
                timestamp=data.timestamp
            )
            telemetry_service.update_debris(debris)
        
        system_status = telemetry_service.get_system_status()
        
        return {
            "status": "success",
            "message": f"Telemetry updated for {data.object_id}",
            "system_status": system_status
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/telemetry/satellites")
async def get_satellites():
    """Get all satellite telemetry"""
    satellites = telemetry_service.get_all_satellites()
    return {"count": len(satellites), "satellites": satellites}

@router.get("/telemetry/debris")
async def get_debris():
    """Get all debris telemetry"""
    debris = telemetry_service.get_all_debris()
    return {"count": len(debris), "debris": debris}

@router.get("/telemetry/status")
async def get_status():
    """Get system status"""
    return telemetry_service.get_system_status()
