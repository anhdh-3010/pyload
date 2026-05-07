from app.api.v1.accounts.domain.models import Accounts
from core.repository import BaseRepository


class AccountRepository(BaseRepository[Accounts]):
    model_class = Accounts
