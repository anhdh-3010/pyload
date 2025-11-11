from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import Header, Depends
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import config
from core.exceptions import CustomException
from core.database.session import get_async_session


class JWTDecodeError(CustomException):
    code = 401
    message = "Invalid token"


class JWTExpiredError(CustomException):
    code = 401
    message = "Token expired"


class UserNotFoundError(CustomException):
    code = 401
    message = "User not found"


class JWTHandler:
    secret_key = config.jwt_secret_key
    algorithm = config.jwt_algorithm
    expire_minutes = config.jwt_access_token_expire_minutes

    @staticmethod
    def encode(payload: dict, auth_method="password") -> str:
        expire = datetime.now(UTC) + timedelta(minutes=JWTHandler.expire_minutes)
        payload.update({"exp": expire, "auth_method": auth_method})
        return jwt.encode(
            payload, JWTHandler.secret_key, algorithm=JWTHandler.algorithm
        )

    @staticmethod
    def decode(token: str) -> dict:
        try:
            return jwt.decode(
                token, JWTHandler.secret_key, algorithms=[JWTHandler.algorithm]
            )
        except ExpiredSignatureError as exception:
            raise JWTExpiredError() from exception
        except JWTError as exception:
            raise JWTDecodeError() from exception

    @staticmethod
    def decode_expired(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                JWTHandler.secret_key,
                algorithms=[JWTHandler.algorithm],
                options={"verify_exp": False},
            )
        except JWTError as exception:
            raise JWTDecodeError() from exception

    @staticmethod
    async def get_current_user(
        authorization: str = Header(None, alias="Authorization"),
        db_session: AsyncSession = Depends(get_async_session),
    ):
        """
        Get current authenticated user from JWT token.
        Returns User object from database.
        """
        from app.users.data_access.user_repository import UserRepository

        if not authorization:
            raise JWTDecodeError()

        # Extract token from "Bearer <token>" format
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise JWTDecodeError()

        token = parts[1]
        payload = JWTHandler.decode(token)

        # Get user_id from payload
        user_id = payload.get("user_id")
        if not user_id:
            raise JWTDecodeError()

        # Fetch user from database
        user_repo = UserRepository(db_session)
        try:
            user = await user_repo.get_by_id(UUID(user_id))
        except ValueError:
            raise JWTDecodeError()

        if not user:
            raise UserNotFoundError()

        return user
