"""Shared FastAPI dependencies."""

from fastapi import Depends

from app.core.security import get_current_user

CurrentUser = Depends(get_current_user)


async def get_business_scope(current_user=CurrentUser):
    return {"business_id": current_user.get("business_id")}
