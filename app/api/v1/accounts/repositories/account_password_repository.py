from app.api.v1.accounts.domain.models import AccountPasswords
from core.repository import BaseRepository


class AccountPasswordRepository(BaseRepository[AccountPasswords]):
    model_class = AccountPasswords
