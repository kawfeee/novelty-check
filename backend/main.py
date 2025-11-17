from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ingest, novelty
from db import init_db
import uvicorn

app = FastAPI(
    title="Novelty Score Engine",
    description="R&D Proposal Novelty Detection System",
    version="1.0.0"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest.router, prefix="/api", tags=["Ingestion"])
app.include_router(novelty.router, prefix="/api", tags=["Novelty"])

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await init_db()

@app.get("/")
async def root():
    return {
        "message": "Novelty Score Engine API",
        "version": "1.0.0",
        "endpoints": {
            "ingest": "/api/ingest",
            "novelty": "/api/novelty"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
