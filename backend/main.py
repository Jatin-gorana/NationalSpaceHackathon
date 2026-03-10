from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
from api.telemetry_api import router as telemetry_router
from api.maneuver_api import router as maneuver_router
from api.simulation_api import router as simulation_router
from api.maneuver_schedule_api import router as maneuver_schedule_router
from api.ai_optimization_api import router as ai_optimization_router
from services.simulation_engine import simulation_engine

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"🔌 WebSocket client disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                dead_connections.append(connection)
        
        # Clean up dead connections
        for conn in dead_connections:
            self.disconnect(conn)

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start simulation engine
    print("🚀 Starting ACM System...")
    await simulation_engine.start()
    
    # Start broadcast task (20 Hz = 50ms)
    async def broadcast_loop():
        while True:
            try:
                if len(manager.active_connections) > 0:
                    state = simulation_engine.get_state()
                    await manager.broadcast(state)
                await asyncio.sleep(0.05)  # 50ms = 20 Hz
            except Exception as e:
                print(f"❌ Broadcast error: {e}")
                await asyncio.sleep(0.05)
    
    broadcast_task = asyncio.create_task(broadcast_loop())
    print("📡 WebSocket broadcast started (20 Hz)")
    
    yield
    
    # Shutdown: Stop simulation engine
    print("🛑 Shutting down ACM System...")
    broadcast_task.cancel()
    await simulation_engine.stop()

app = FastAPI(
    title="Autonomous Constellation Manager",
    description="AI-powered satellite collision avoidance and orbital management system",
    version="2.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(telemetry_router, prefix="/api", tags=["telemetry"])
app.include_router(maneuver_router, prefix="/api", tags=["maneuvers"])
app.include_router(simulation_router, prefix="/api", tags=["simulation"])
app.include_router(maneuver_schedule_router, prefix="/api", tags=["maneuver-scheduling"])
app.include_router(ai_optimization_router, prefix="/api", tags=["ai-optimization"])

@app.get("/")
async def root():
    state = simulation_engine.get_state()
    return {
        "status": "ACM System Online", 
        "version": "2.1.0",
        "features": ["AI Optimization", "Real-time Visualization", "Genetic Algorithms", "WebSocket Updates"],
        "simulation": {
            "running": simulation_engine.running,
            "update_rate": "20 Hz (50ms)",
            "satellites": len(state["satellites"]),
            "debris": len(state["debris"]),
            "threats": state["threats"]
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "simulation_running": simulation_engine.running,
        "update_interval": simulation_engine.update_interval
    }

@app.get("/debug/force-collisions")
async def force_collisions():
    """Debug endpoint to force collision detection and show results"""
    simulation_engine.detect_collisions()
    
    satellites = telemetry_service.get_all_satellites()
    at_risk = [sat for sat in satellites if sat.object_id in simulation_engine.collision_risks]
    
    return {
        "total_satellites": len(satellites),
        "satellites_at_risk": len(at_risk),
        "threat_count": simulation_engine.threat_count,
        "collision_risks": list(simulation_engine.collision_risks),
        "at_risk_satellites": [
            {
                "id": sat.object_id,
                "status": sat.status,
                "position": sat.position,
                "fuel": sat.fuel_remaining
            }
            for sat in at_risk
        ]
    }

@app.get("/debug/collision-debris")
async def get_collision_debris():
    """Debug endpoint to show collision debris objects"""
    debris = telemetry_service.get_all_debris()
    collision_debris = [
        {
            "id": deb.object_id,
            "position": deb.position,
            "velocity": deb.velocity,
            "size": deb.size_estimate
        }
        for deb in debris 
        if "IMMEDIATE" in deb.object_id or "CROSS" in deb.object_id or "CHASE" in deb.object_id
    ]
    
    return {
        "total_debris": len(debris),
        "collision_debris_count": len(collision_debris),
        "collision_debris": collision_debris
    }

@app.websocket("/ws/simulation")
async def websocket_simulation(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state immediately
        await websocket.send_json(simulation_engine.get_state())
        
        # Keep connection alive and handle pings
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # No message received, continue
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket)
