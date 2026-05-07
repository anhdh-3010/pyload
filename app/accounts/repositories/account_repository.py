from app.accounts.domain.models import Accounts
from core.repository import BaseRepository


class AccountRepository(BaseRepository[Accounts]):
    model_class = Accounts
