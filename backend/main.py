from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.telemetry_api import router as telemetry_router
from api.maneuver_api import router as maneuver_router
from api.simulation_api import router as simulation_router

app = FastAPI(
    title="Autonomous Constellation Manager",
    description="Satellite collision avoidance and orbital management system",
    version="1.0.0"
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

@app.get("/")
async def root():
    return {"status": "ACM System Online", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
