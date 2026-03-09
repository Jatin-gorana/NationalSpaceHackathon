from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.telemetry_api import router as telemetry_router
from api.maneuver_api import router as maneuver_router
from api.simulation_api import router as simulation_router
from api.maneuver_schedule_api import router as maneuver_schedule_router
from api.ai_optimization_api import router as ai_optimization_router

app = FastAPI(
    title="Autonomous Constellation Manager",
    description="AI-powered satellite collision avoidance and orbital management system",
    version="2.1.0"
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
        "features": ["AI Optimization", "Real-time Visualization", "Genetic Algorithms"]
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
