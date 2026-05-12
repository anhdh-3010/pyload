from core.repository.base import BaseRepository
from modules.accounts.domain.models import Accounts


class AccountRepository(BaseRepository[Accounts]):
    model_class = Accounts
