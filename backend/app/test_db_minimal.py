"""
Minimal database connection test
This will help identify if it's a connection issue or a schema creation issue
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


async def test_basic_connection():
    """Test just connecting to database without creating tables"""
    print("Testing basic database connection...")
    
    from app.config import get_settings
    from sqlalchemy.ext.asyncio import create_async_engine
    
    settings = get_settings()
    print(f"DATABASE_URL: {settings.DATABASE_URL[:50]}...")
    
    # Create engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,  # Test connections before using
        pool_size=1,
        max_overflow=0
    )
    
    print("Engine created, attempting connection...")
    
    try:
        # Try to connect and execute simple query
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            row = result.fetchone()
            print(f"✅ Connection successful! Result: {row}")
            
        await engine.dispose()
        print("✅ Engine disposed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"\nError type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


async def test_with_timeout():
    """Test with a timeout to prevent hanging"""
    try:
        result = await asyncio.wait_for(
            test_basic_connection(),
            timeout=10.0
        )
        return result
    except asyncio.TimeoutError:
        print("❌ Connection timed out after 10 seconds!")
        print("\nThis means the database is not reachable or taking too long to respond")
        return False


async def main():
    print("="*60)
    print("Database Connection Test (10 second timeout)")
    print("="*60)
    print()
    
    success = await test_with_timeout()
    
    print()
    print("="*60)
    if success:
        print("✅ Database connection works!")
        print("\nThe hang is likely in the table creation (init_db)")
        print("Try using the fixed database.py")
    else:
        print("❌ Database connection failed!")
        print("\nPossible fixes:")
        print("1. Check if DATABASE_URL is correct")
        print("2. Check if Supabase project is active")
        print("3. Try connecting with psql:")
        print("   psql 'postgresql://...'")
        print("4. Check firewall/network settings")
        print("5. Try direct connection (not pooler):")
        print("   Use port 5432 instead of 6543")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())