from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseRepository
from ..domain.models import User


class UserRepository(BaseRepository[User]):
    def __init__(self, db_session: AsyncSession) -> None:
        super().__init__(User, db_session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email using filter method"""
        users = await self.filter(filter_conditions=[User.email == email], limit=1)
        return users[0] if users else None

    async def create_or_update_from_google(
        self, email: str, full_name: Optional[str] = None, avatar: Optional[str] = None
    ) -> User:
        """Create new user or update existing user from Google OAuth data"""
        user = await self.get_by_email(email)

        if user:
            # Update existing user
            if full_name:
                user.full_name = full_name
            if avatar:
                user.avatar = avatar
            await self.session.flush()
            return user
        else:
            # Create new user
            user_data = {
                "email": email,
                "full_name": full_name,
                "avatar": avatar,
            }
            return await self.create(user_data)
