import asyncpg
import os
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection pool
pool: Optional[asyncpg.Pool] = None

async def init_db():
    """Initialize database connection pool"""
    global pool
    
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/novelty_db"
    )
    
    pool = await asyncpg.create_pool(
        database_url,
        min_size=2,
        max_size=10
    )
    print("✅ Database connection pool created")

async def close_db():
    """Close database connection pool"""
    global pool
    if pool:
        await pool.close()
        print("Database connection pool closed")

@asynccontextmanager
async def get_db():
    """Get database connection from pool"""
    if pool is None:
        raise RuntimeError("Database pool not initialized")
    
    async with pool.acquire() as connection:
        yield connection

async def insert_proposal(
    title: str,
    full_text: str,
    embedding: List[float]
) -> int:
    """
    Insert a new proposal into the database
    
    Args:
        title: Proposal title
        full_text: Full proposal text
        embedding: 768-dimensional embedding vector
        
    Returns:
        ID of inserted proposal
    """
    async with get_db() as conn:
        result = await conn.fetchrow(
            """
            INSERT INTO proposals (title, full_text, embedding)
            VALUES ($1, $2, $3::vector)
            RETURNING id
            """,
            title,
            full_text,
            str(embedding)
        )
        return result['id']

async def find_similar_proposals(
    embedding: List[float],
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Find most similar proposals using cosine similarity
    
    Args:
        embedding: Query embedding vector
        limit: Number of similar proposals to return
        
    Returns:
        List of similar proposals with similarity scores
    """
    async with get_db() as conn:
        results = await conn.fetch(
            """
            SELECT 
                id,
                title,
                1 - (embedding <=> $1::vector) AS similarity
            FROM proposals
            ORDER BY embedding <=> $1::vector
            LIMIT $2
            """,
            str(embedding),
            limit
        )
        
        return [
            {
                "id": row['id'],
                "title": row['title'],
                "similarity": round(float(row['similarity']), 4)
            }
            for row in results
        ]

async def get_proposal_by_id(proposal_id: int) -> Optional[Dict[str, Any]]:
    """Get a proposal by its ID"""
    async with get_db() as conn:
        result = await conn.fetchrow(
            """
            SELECT id, title, full_text, created_at
            FROM proposals
            WHERE id = $1
            """,
            proposal_id
        )
        
        if result:
            return dict(result)
        return None

async def count_proposals() -> int:
    """Get total count of proposals in database"""
    async with get_db() as conn:
        result = await conn.fetchval("SELECT COUNT(*) FROM proposals")
        return result
