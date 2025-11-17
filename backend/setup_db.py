"""
Run database migrations on Render after deployment
Execute this once after your API is deployed
"""
import asyncio
import asyncpg
import os
from pathlib import Path

async def run_migrations():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return
    
    print(f"🔗 Connecting to database...")
    conn = await asyncpg.connect(database_url)
    
    try:
        # Check if vector extension exists
        print("📦 Creating vector extension...")
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("✅ Vector extension installed")
        
        # Run migration 001
        print("\n📄 Running migration 001_init.sql...")
        migration_001 = Path(__file__).parent / "migrations" / "001_init.sql"
        if migration_001.exists():
            sql = migration_001.read_text()
            await conn.execute(sql)
            print("✅ Migration 001 completed")
        else:
            print("⚠️ Migration 001 file not found")
        
        # Run migration 002
        print("\n📄 Running migration 002_refactor_for_api.sql...")
        migration_002 = Path(__file__).parent / "migrations" / "002_refactor_for_api.sql"
        if migration_002.exists():
            sql = migration_002.read_text()
            await conn.execute(sql)
            print("✅ Migration 002 completed")
        else:
            print("⚠️ Migration 002 file not found")
        
        # Verify table exists
        result = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'proposals'
        """)
        
        if result:
            print("\n✅ Database setup complete!")
            print(f"📊 Tables found: {[r['table_name'] for r in result]}")
        else:
            print("\n⚠️ No tables found - migrations may have failed")
            
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        raise
    finally:
        await conn.close()
        print("\n🔌 Database connection closed")

if __name__ == "__main__":
    asyncio.run(run_migrations())
