"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from app.config import get_settings
from app.core.database import init_db
from app.core.cache import init_redis, close_redis
from app.core.logging import setup_logging
from app.api.v1 import webhooks, leads, notifications, voice, auth

settings = get_settings()

# ── Socket.IO for real-time ──
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    setup_logging()
    await init_db()
    await init_redis()
    yield
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent Sales Agent System",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
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

# ── Mount Socket.IO ──
socket_app = socketio.ASGIApp(sio, other_app=app)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}


@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
