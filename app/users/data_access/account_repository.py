from domain.models import Accounts
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseRepository


class AccountRepository(BaseRepository[Accounts]):
    def __init__(self, db_session: AsyncSession) -> None:
        super().__init__(Accounts, db_session)

    def get_by_account_name(self):
        pass
