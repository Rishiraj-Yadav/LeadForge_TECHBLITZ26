# """FastAPI application entry point."""

# from contextlib import asynccontextmanager
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# import socketio

# from app.config import get_settings
# from app.core.database import init_db
# from app.core.cache import init_redis, close_redis
# from app.core.logging import setup_logging
# from app.api.v1 import webhooks, leads, notifications, voice, auth, setup, onboarding

# settings = get_settings()

# # ── Socket.IO for real-time ──
# sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Startup / shutdown events."""
#     setup_logging()
#     await init_db()
#     await init_redis()
#     # Best-effort: register Telegram webhook using API_BASE_URL from .env
#     from app.api.v1.setup import auto_register_telegram_webhook
#     await auto_register_telegram_webhook()
#     yield
#     await close_redis()


# app = FastAPI(
#     title=settings.APP_NAME,
#     description="Intelligent Sales Agent System",
#     version="1.0.0",
#     lifespan=lifespan,
# )

# # ── CORS ──
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://localhost:3001", "https://*.vercel.app"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ── API Routes ──
# app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
# app.include_router(leads.router, prefix="/api/v1/leads", tags=["leads"])
# app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
# app.include_router(voice.router, prefix="/api/v1/voice", tags=["voice"])
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(setup.router, prefix="/api/v1/setup", tags=["setup"])
# app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["onboarding"])

# # ── Mount Socket.IO ──
# socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


# @app.get("/health")
# async def health_check():
#     return {"status": "healthy", "service": settings.APP_NAME}


# @sio.event
# async def connect(sid, environ):
#     print(f"Client connected: {sid}")


# @sio.event
# async def disconnect(sid):
#     print(f"Client disconnected: {sid}")




"""FastAPI application entry point."""

from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from app.config import get_settings
from app.core.database import init_mongodb
from app.core.cache import init_redis, close_redis
from app.core.logging import setup_logging
from app.api.v1 import webhooks, leads, notifications, voice, auth, setup, onboarding

settings = get_settings()

# ── Socket.IO for real-time ──
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events with proper error handling."""
    print(f"\n{'='*60}")
    print(f"🚀 Starting {settings.APP_NAME}")
    print(f"{'='*60}\n")
    
    setup_logging()
    
    # ── 1. Database Connection (with timeout) ──
    print("🔍 Connecting to database...")
    try:
        await asyncio.wait_for(init_mongodb(), timeout=10.0)
        print("✅ Database connected successfully")
    except asyncio.TimeoutError:
        print("❌ Database connection TIMEOUT (10s)")
        print("⚠️  Continuing without database - some features will not work")
        print("💡 Check your MONGODB_URL in .env")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("⚠️  Continuing without database - some features will not work")
    
    # ── 2. Redis Connection (with timeout) ──
    print("\n🔍 Connecting to Redis...")
    try:
        await asyncio.wait_for(init_redis(), timeout=5.0)
        print("✅ Redis connected successfully")
    except asyncio.TimeoutError:
        print("❌ Redis connection TIMEOUT (5s)")
        print("⚠️  Continuing without Redis - caching disabled")
        print("💡 Start Redis: docker run -d -p 6379:6379 redis")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("⚠️  Continuing without Redis - caching disabled")
    
    # ── 3. Telegram Webhook (non-blocking, with timeout) ──
    if settings.TELEGRAM_BOT_TOKEN and settings.API_BASE_URL:
        print("\n🔍 Registering Telegram webhook...")
        
        async def register_webhook_background():
            """Register webhook in background with timeout."""
            try:
                from app.api.v1.setup import auto_register_telegram_webhook
                
                await asyncio.wait_for(
                    auto_register_telegram_webhook(), 
                    timeout=5.0
                )
                print("✅ Telegram webhook registered successfully")
                print(f"   Webhook URL: {settings.API_BASE_URL}/api/v1/webhooks/telegram")
            except asyncio.TimeoutError:
                print("⚠️  Telegram webhook registration timed out (5s)")
                print(f"   Webhook URL: {settings.API_BASE_URL}/api/v1/webhooks/telegram")
                print("   You can register manually later at: POST /api/v1/setup/telegram-webhook")
            except Exception as e:
                print(f"⚠️  Telegram webhook registration failed: {e}")
                print("   This is OK - the bot will still work")
                print("   You can register manually later at: POST /api/v1/setup/telegram-webhook")
        
        # Run in background task (doesn't block startup)
        asyncio.create_task(register_webhook_background())
    else:
        print("\n⚠️  Telegram webhook skipped")
        if not settings.TELEGRAM_BOT_TOKEN:
            print("   Missing: TELEGRAM_BOT_TOKEN in .env")
        if not settings.API_BASE_URL:
            print("   Missing: API_BASE_URL in .env")
    
    print(f"\n{'='*60}")
    print(f"✨ {settings.APP_NAME} is READY!")
    print(f"{'='*60}")
    print(f"\n📝 API Docs: http://localhost:8005/docs")
    print(f"🏥 Health Check: http://localhost:8005/health")
    if settings.API_BASE_URL:
        print(f"🔗 Webhook URL: {settings.API_BASE_URL}/api/v1/webhooks/telegram")
    print()
    
    yield
    
    # ── Shutdown ──
    print(f"\n🛑 Shutting down {settings.APP_NAME}...")
    try:
        await close_redis()
        print("✅ Redis connection closed")
    except Exception as e:
        print(f"⚠️  Error closing Redis: {e}")
    print("👋 Goodbye!\n")


app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent Sales Agent System",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "https://*.vercel.app",
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes ──
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(leads.router, prefix="/api/v1/leads", tags=["leads"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(voice.router, prefix="/api/v1/voice", tags=["voice"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(setup.router, prefix="/api/v1/setup", tags=["setup"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["onboarding"])

# ── Mount Socket.IO ──
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV
    }


@sio.event
async def connect(sid, environ):
    """Socket.IO client connected"""
    print(f"🔌 Socket.IO client connected: {sid}")


@sio.event
async def disconnect(sid):
    """Socket.IO client disconnected"""
    print(f"🔌 Socket.IO client disconnected: {sid}")
    
    