"""
Database connection and session management
"""
import os
from contextlib import asynccontextmanager
from prisma import Prisma
from app.core.config import settings

# Global database client
db_client = None

async def connect_database():
    """Initialize database connection"""
    global db_client
    
    if db_client is None:
        db_client = Prisma(
            datasource={
                "url": settings.DATABASE_URL
            }
        )
        await db_client.connect()
    
    return db_client

async def disconnect_database():
    """Close database connection"""
    global db_client
    
    if db_client is not None:
        await db_client.disconnect()
        db_client = None

@asynccontextmanager
async def get_db():
    """Get database session"""
    client = await connect_database()
    try:
        yield client
    finally:
        # Keep connection alive for reuse
        pass

async def init_database():
    """Initialize database with required tables"""
    try:
        await connect_database()
        # Database initialization logic here
        # Tables should be created via Prisma migrations
        print("Database connection established successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise

async def health_check_database():
    """Check database health"""
    try:
        client = await connect_database()
        # Simple query to check connection
        result = await client.query_raw("SELECT 1 as test")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
