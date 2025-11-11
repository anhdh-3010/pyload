from datetime import UTC, datetime, timedelta

from fastapi import Header
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import config
from app.core.exceptions import CustomException


class JWTDecodeError(CustomException):
    code = 401
    message = "Invalid token"


class JWTExpiredError(CustomException):
    code = 401
    message = "Token expired"


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
        authorization: str = Header(None, alias="Authorization")
    ) -> dict:
        if not authorization:
            raise JWTDecodeError()

        # Extract token from "Bearer <token>" format
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise JWTDecodeError()

        token = parts[1]
        payload = JWTHandler.decode(token)
        return payload
