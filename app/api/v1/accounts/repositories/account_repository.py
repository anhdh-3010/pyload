from app.api.v1.accounts.domain.models import Accounts
from core.repository.base import BaseRepository


class AccountRepository(BaseRepository[Accounts]):
    model_class = Accounts
