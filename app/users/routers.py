from fastapi import APIRouter, Depends

from app.users.domain import (
    User,
    UserResponse,
)
from core import (
    JWTHandler,
)

router = APIRouter()
private_router = APIRouter(dependencies=[Depends(JWTHandler.get_current_user)])


@private_router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(JWTHandler.get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)
