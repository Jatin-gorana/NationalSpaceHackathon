"""In-memory storage for satellite and debris telemetry"""
from typing import Dict, List, Union
from models.satellite import Satellite
from models.debris import Debris
from datetime import datetime

class TelemetryService:
    def __init__(self):
        self.satellites: Dict[str, Satellite] = {}
        self.debris: Dict[str, Debris] = {}
    
    def update_satellite(self, satellite: Satellite) -> None:
        """Store or update satellite telemetry"""
        self.satellites[satellite.object_id] = satellite
    
    def update_debris(self, debris: Debris) -> None:
        """Store or update debris telemetry"""
        self.debris[debris.object_id] = debris
    
    def get_satellite(self, object_id: str) -> Union[Satellite, None]:
        """Retrieve satellite by ID"""
        return self.satellites.get(object_id)
    
    def get_debris(self, object_id: str) -> Union[Debris, None]:
        """Retrieve debris by ID"""
        return self.debris.get(object_id)
    
    def get_all_satellites(self) -> List[Satellite]:
        """Get all satellites"""
        return list(self.satellites.values())
    
    def get_all_debris(self) -> List[Debris]:
        """Get all debris"""
        return list(self.debris.values())
    
    def get_system_status(self) -> Dict:
        """Get overall system status"""
        return {
            "total_satellites": len(self.satellites),
            "total_debris": len(self.debris),
            "operational_satellites": sum(1 for s in self.satellites.values() if s.status == "operational"),
            "critical_satellites": sum(1 for s in self.satellites.values() if s.status == "critical"),
            "timestamp": datetime.utcnow().isoformat()
        }

# Global instance
telemetry_service = TelemetryService()
