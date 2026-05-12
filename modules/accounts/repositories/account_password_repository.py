from core.repository.base import BaseRepository
from modules.accounts.domain.models import AccountPasswords


class AccountPasswordRepository(BaseRepository[AccountPasswords]):
    model_class = AccountPasswords
