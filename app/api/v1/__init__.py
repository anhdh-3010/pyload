from fastapi import APIRouter

from app.api.v1.users.routers import router as auth_router
from app.api.v1.users.routers import private_router

v1_router = APIRouter()
v1_router.include_router(auth_router)
