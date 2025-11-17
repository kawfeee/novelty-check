from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers import novelty_check
from db import init_db
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database connection on startup"""
    await init_db()
    yield

app = FastAPI(
    title="Novelty Score API",
    description="API-only microservice for R&D proposal novelty detection",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration (optional - enable if needed for cross-origin requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include novelty check router
app.include_router(novelty_check.router, prefix="/api", tags=["Novelty"])

@app.get("/")
async def root():
    return {
        "service": "Novelty Score API",
        "version": "2.0.0",
        "endpoint": "/api/novelty-check",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "novelty-score-api"}

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
