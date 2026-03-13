"""Simple auth endpoints for scaffold use."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.core.security import create_access_token, hash_password, verify_password

router = APIRouter()

_USERS: dict[str, dict] = {}


class SignupPayload(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    business_id: str | None = None


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup")
async def signup(payload: SignupPayload):
    if payload.email in _USERS:
        raise HTTPException(status_code=400, detail="User already exists")
    _USERS[payload.email] = {
        "email": payload.email,
        "hashed_password": hash_password(payload.password),
        "full_name": payload.full_name,
        "business_id": payload.business_id,
    }
    return {"message": "User created"}


@router.post("/login")
async def login(payload: LoginPayload):
    user = _USERS.get(payload.email)
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": payload.email, "business_id": user.get("business_id")})
    return {"access_token": token, "token_type": "bearer"}
