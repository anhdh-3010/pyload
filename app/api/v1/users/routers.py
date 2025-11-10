from fastapi import APIRouter, Request

from app.api.v1.users.domain.schemas import Token
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.core.security.auth import JWTHandler
from app.core.security.google_auth import oauth

router = APIRouter()


@router.get("/auth/google")
async def auth_google(request: Request):
    return await oauth.google.authorize_redirect(
        request, redirect_uri="http://localhost:8000/auth/google/callback"
    )


@router.get("/auth/google/callback", response_model=Token)
async def auth_google_callback(request: Request) -> Token:
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo") or {}
        return Token(
            access_token=JWTHandler.encode(
                payload={"user_info": user_info}, auth_method="google"
            ),
            refresh_token=JWTHandler.encode(
                payload={"sub": "refresh_token"}, auth_method="google"
            ),
        )
    except Exception:
        raise BadRequestException("Could not validate credentials")


async def refresh_token_access(access_token: str, refresh_token: str) -> Token:
    token = JWTHandler.decode(access_token)
    refresh_token = JWTHandler.decode(refresh_token)

    if refresh_token.get("sub") != "refresh_token":
        raise UnauthorizedException("Invalid refresh token")

    return Token(
        access_token=JWTHandler.encode(
            payload={"user_info": token.get("userinfo")}, auth_method="google"
        ),
        refresh_token=JWTHandler.encode(
            payload={"sub": "refresh_token"}, auth_method="google"
        ),
    )
