"""
Quick Diagnostic - Find what's causing the startup hang
Run this before starting the server
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


async def test_component(name: str, test_func, timeout: float = 5.0):
    """Test a component with timeout"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    try:
        result = await asyncio.wait_for(test_func(), timeout=timeout)
        print(f"✅ {name} - PASSED")
        return True
    except asyncio.TimeoutError:
        print(f"❌ {name} - TIMEOUT ({timeout}s)")
        print(f"   This component is BLOCKING startup!")
        return False
    except Exception as e:
        print(f"⚠️  {name} - FAILED: {e}")
        return False


async def test_database():
    """Test database connection"""
    from app.core.database import init_db
    await init_db()
    print("   Database connection established")


async def test_redis():
    """Test Redis connection"""
    from app.core.cache import init_redis
    await init_redis()
    print("   Redis connection established")


async def test_telegram_webhook():
    """Test Telegram webhook registration"""
    from app.api.v1.setup import auto_register_telegram_webhook
    await auto_register_telegram_webhook()
    print("   Telegram webhook registered")


async def test_telegram_basic():
    """Test basic Telegram API connectivity"""
    from app.config import get_settings
    import httpx
    
    settings = get_settings()
    
    if not settings.TELEGRAM_BOT_TOKEN:
        raise Exception("TELEGRAM_BOT_TOKEN not set")
    
    async with httpx.AsyncClient(timeout=3.0) as client:
        response = await client.get(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getMe"
        )
        data = response.json()
        
        if data.get("ok"):
            bot_info = data.get("result", {})
            print(f"   Bot: @{bot_info.get('username')}")
        else:
            raise Exception(f"Invalid response: {data}")


async def test_config():
    """Test configuration loading"""
    from app.config import get_settings
    
    settings = get_settings()
    
    required = {
        "TELEGRAM_BOT_TOKEN": settings.TELEGRAM_BOT_TOKEN,
        "DATABASE_URL": settings.DATABASE_URL,
        "API_BASE_URL": settings.API_BASE_URL,
        "GOOGLE_API_KEY": settings.GOOGLE_API_KEY,
    }
    
    missing = [k for k, v in required.items() if not v]
    
    if missing:
        raise Exception(f"Missing: {', '.join(missing)}")
    
    print(f"   All required env vars present")
    print(f"   API_BASE_URL: {settings.API_BASE_URL}")


async def main():
    print("\n" + "="*60)
    print("🔍 LeadForge Startup Diagnostic")
    print("="*60)
    print("\nThis will identify which component is causing the hang...\n")
    
    results = {}
    
    # Test 1: Configuration
    results["Config"] = await test_component(
        "Configuration (.env)",
        test_config,
        timeout=2.0
    )
    
    # Test 2: Database
    results["Database"] = await test_component(
        "Database (Supabase)",
        test_database,
        timeout=10.0
    )
    
    # Test 3: Redis
    results["Redis"] = await test_component(
        "Redis",
        test_redis,
        timeout=5.0
    )
    
    # Test 4: Telegram Basic (just check bot is valid)
    results["Telegram API"] = await test_component(
        "Telegram API (getMe)",
        test_telegram_basic,
        timeout=3.0
    )
    
    # Test 5: Telegram Webhook (this is likely the culprit)
    results["Telegram Webhook"] = await test_component(
        "Telegram Webhook Registration",
        test_telegram_webhook,
        timeout=5.0
    )
    
    # Summary
    print(f"\n\n{'='*60}")
    print("📊 SUMMARY")
    print("="*60)
    
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{component:.<40} {status}")
    
    print("="*60)
    
    # Find the problem
    failed = [k for k, v in results.items() if not v]
    
    if not failed:
        print("\n🎉 All tests passed! You should be able to start the server.")
        print("\nStart command:")
        print("   uvicorn app.main:socket_app --host 0.0.0.0 --port 8005 --reload")
    else:
        print(f"\n🔴 {len(failed)} component(s) failed or timed out:")
        for component in failed:
            print(f"   • {component}")
        
        print("\n💡 FIXES:")
        
        if "Database" in failed:
            print("\n📦 DATABASE:")
            print("   1. Check DATABASE_URL in .env")
            print("   2. Try simpler connection string (remove prepared_statement params)")
            print("   3. Test connection: psql <DATABASE_URL>")
        
        if "Redis" in failed:
            print("\n📦 REDIS:")
            print("   1. Start Redis: docker run -d -p 6379:6379 redis")
            print("   2. Or comment out Redis code for now")
        
        if "Telegram Webhook" in failed:
            print("\n📦 TELEGRAM WEBHOOK (most likely cause!):")
            print("   1. Your ngrok URL might be expired/inactive")
            print("   2. Start new ngrok: ngrok http 8005")
            print("   3. Update API_BASE_URL in .env with new ngrok URL")
            print("   4. OR use the fixed main.py which has timeout handling")
        
        if "Telegram API" in failed:
            print("\n📦 TELEGRAM API:")
            print("   1. Check TELEGRAM_BOT_TOKEN in .env is correct")
            print("   2. Verify bot exists: open https://t.me/leadforge12_bot")
    
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()