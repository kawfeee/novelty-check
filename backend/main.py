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
    # Auto-setup database on first run
    await setup_database()
    yield

async def setup_database():
    """Setup database tables and extensions on first run"""
    from db import pool
    from pathlib import Path
    
    if pool is None:
        print("⚠️ Database pool not initialized, skipping setup")
        return
    
    async with pool.acquire() as conn:
        try:
            # Install pgvector extension
            print("📦 Installing pgvector extension...")
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("✅ pgvector extension ready")
            
            # Check if proposals table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'proposals'
                );
            """)
            
            if not table_exists:
                print("📄 Running initial migrations...")
                
                # Run migration 001
                migration_001 = Path(__file__).parent / "migrations" / "001_init.sql"
                if migration_001.exists():
                    sql = migration_001.read_text()
                    await conn.execute(sql)
                    print("✅ Migration 001 completed")
                
                # Run migration 002
                migration_002 = Path(__file__).parent / "migrations" / "002_refactor_for_api.sql"
                if migration_002.exists():
                    sql = migration_002.read_text()
                    await conn.execute(sql)
                    print("✅ Migration 002 completed")
                
                print("✅ Database setup complete!")
            else:
                print("✅ Database already initialized")
                
        except Exception as e:
            print(f"⚠️ Database setup error (may be normal if already setup): {e}")

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
