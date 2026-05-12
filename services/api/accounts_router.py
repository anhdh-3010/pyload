from fastapi import APIRouter, Depends

from core import JWTHandler
from modules.accounts.domain.dependencies import AccountServiceDep
from modules.accounts.domain.schemas import (
    AccountResponse,
    LoginRequest,
    RegisterRequest,
    Token,
)

router = APIRouter()
private_router = APIRouter()


@router.post("/register", response_model=Token, tags=["auth"])
async def register(request: RegisterRequest, account_service: AccountServiceDep) -> Token:
    account = await account_service.register(request)
    token = JWTHandler.encode({"user_id": str(account.id)})
    return Token(access_token=token)


@router.post("/login", response_model=Token, tags=["auth"])
async def login(request: LoginRequest, account_service: AccountServiceDep) -> Token:
    account = await account_service.login(request)
    token = JWTHandler.encode({"user_id": str(account.id)})
    return Token(access_token=token)


@private_router.get("/me", response_model=AccountResponse, tags=["accounts"])
async def get_current_user(current_user=Depends(JWTHandler.get_current_user)) -> AccountResponse:
    return AccountResponse(
        id=str(current_user.id),
        account_name=current_user.account_name,
    )
