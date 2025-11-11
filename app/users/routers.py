from fastapi import APIRouter, Request, Depends

# Core imports - much shorter now!
from core import (
    JWTHandler,
    oauth,
    config,
    Transactional,
    UnauthorizedException,
    BadRequestException,
)

# Domain imports - also shorter!
from app.users.domain import (
    User,
    Token,
    TokenWithUser,
    UserResponse,
    UserServiceDep,
)

router = APIRouter()
private_router = APIRouter(dependencies=[Depends(JWTHandler.get_current_user)])


@router.get("/auth/google")
async def auth_google(request: Request):
    redirect_uri = f"{config.base_url}/api/v1/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri=redirect_uri)


@router.get("/auth/google/callback", response_model=TokenWithUser)
@Transactional()
async def auth_google_callback(
    request: Request, user_service: UserServiceDep
) -> TokenWithUser:
    try:
        # Get access token from Google
        token = await oauth.google.authorize_access_token(request)

        # Get user info from Google
        user_info = token.get("userinfo")
        if not user_info:
            raise BadRequestException("Failed to get user info from Google")

        # Handle login through service layer (creates/updates user in DB)
        user, access_token, refresh_token = await user_service.handle_google_login(
            user_info
        )

        # Return tokens with user info
        return TokenWithUser(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )
    except Exception as e:
        print(f"OAuth callback error: {type(e).__name__}: {str(e)}")
        raise BadRequestException(str(e))


@private_router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(JWTHandler.get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@private_router.post("/auth/refresh", response_model=Token)
async def refresh_token_access(payload: Token) -> Token:
    token = JWTHandler.decode(payload.access_token)
    refresh_token = JWTHandler.decode(payload.refresh_token)

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
