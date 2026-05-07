from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt

from core.config import config
from core.database.session import get_unit_of_work
from core.exceptions import CustomException
from core.unit_of_work import UnitOfWork


class JWTDecodeError(CustomException):
    code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid token"


class JWTExpiredError(CustomException):
    code = status.HTTP_401_UNAUTHORIZED
    message = "Token expired"


class UserNotFoundError(CustomException):
    code = status.HTTP_401_UNAUTHORIZED
    message = "User not found"


class JWTHandler:
    secret_key = config.jwt_secret_key
    algorithm = config.jwt_algorithm
    expire_minutes = config.jwt_access_token_expire_minutes
    bearer_scheme = HTTPBearer()

    @staticmethod
    def encode(payload: dict, auth_method="password") -> str:
        expire = datetime.now(UTC) + timedelta(minutes=JWTHandler.expire_minutes)
        payload.update({"exp": expire, "auth_method": auth_method})
        return jwt.encode(payload, JWTHandler.secret_key, algorithm=JWTHandler.algorithm)

    @staticmethod
    def decode(token: str) -> dict:
        try:
            return jwt.decode(token, JWTHandler.secret_key, algorithms=[JWTHandler.algorithm])
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
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        uow: UnitOfWork = Depends(dependency=get_unit_of_work),
    ):
        """
        Get current authenticated user from JWT token.
        Returns User object from database.
        """
        from app.accounts.repositories import AccountRepository

        if not credentials or not credentials.credentials:
            raise JWTDecodeError()

        payload = JWTHandler.decode(credentials.credentials)

        # Get account_name from payload
        user_id = payload.get("user_id")
        if not user_id:
            raise JWTDecodeError()

        # Fetch user from database
        account_repo = uow.get_repository(AccountRepository)
        try:
            user = await account_repo.get_by_id(UUID(user_id))
        except ValueError as err:
            raise JWTDecodeError() from err

        if not user:
            raise UserNotFoundError()

        return user
