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
