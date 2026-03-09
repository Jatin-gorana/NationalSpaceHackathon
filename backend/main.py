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
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start simulation engine
    await simulation_engine.start()
    
    # Start broadcast task
    async def broadcast_loop():
        while True:
            try:
                state = simulation_engine.get_state()
                await manager.broadcast(state)
                await asyncio.sleep(1)  # Broadcast every second
            except Exception as e:
                print(f"Broadcast error: {e}")
                await asyncio.sleep(1)
    
    broadcast_task = asyncio.create_task(broadcast_loop())
    
    yield
    
    # Shutdown: Stop simulation engine
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
    return {
        "status": "ACM System Online", 
        "version": "2.1.0",
        "features": ["AI Optimization", "Real-time Visualization", "Genetic Algorithms", "WebSocket Updates"],
        "simulation": {
            "running": simulation_engine.running,
            "satellites": len(simulation_engine.get_state()["satellites"]),
            "debris": len(simulation_engine.get_state()["debris"])
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "simulation_running": simulation_engine.running}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state
        await websocket.send_json(simulation_engine.get_state())
        
        # Keep connection alive
        while True:
            # Wait for ping from client
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
