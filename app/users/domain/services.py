from typing import Any, Dict, Optional

from core import JWTHandler, Transactional

from ..data_access.user_repository import UserRepository
from .models import User


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    @Transactional
    async def handle_google_login(
        self, user_info: Dict[str, Any]
    ) -> tuple[User, str, str]:
        """
        Handle Google OAuth login:
        1. Get user info from Google
        2. Create or update user in database
        3. Generate JWT tokens

        Returns: (user, access_token, refresh_token)
        """
        email = user_info.get("email")
        if not email:
            raise ValueError("Email not found in Google user info")

        full_name = user_info.get("name")
        avatar = user_info.get("picture")

        # Create or update user in database
        user = await self.create_or_update_from_google(
            email=email, full_name=full_name, avatar=avatar
        )

        # Generate tokens
        access_token = JWTHandler.encode(
            payload={
                "user_id": str(user.id),
                "email": user.email,
            },
            auth_method="google",
        )

        refresh_token = JWTHandler.encode(
            payload={
                "sub": "refresh_token",
                "user_id": str(user.id),
            },
            auth_method="google",
        )

        return user, access_token, refresh_token

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.user_repository.get_by_email(email)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return await self.user_repository.get_by_id(user_id)

    async def create_or_update_from_google(
        self, email: str, full_name: Optional[str] = None, avatar: Optional[str] = None
    ) -> User:
        """Create new user or update existing user from Google OAuth data"""
        user = await self.user_repository.get_by_email(email)

        if user:
            # Update existing user
            update_data = {}
            if full_name:
                update_data["full_name"] = full_name
            if avatar:
                update_data["avatar"] = avatar
            if update_data:
                await self.user_repository.update(user.id, update_data)
            return user
        else:
            # Create new user
            user_data = {
                "email": email,
                "full_name": full_name,
                "avatar": avatar,
            }
            return await self.user_repository.create(user_data)
