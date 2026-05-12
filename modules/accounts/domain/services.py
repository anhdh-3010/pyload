from fastapi import status

from core import UnitOfWork
from core.exceptions import CustomException
from core.security.password import PasswordHandler
from modules.accounts.domain.models import AccountPasswords, Accounts
from modules.accounts.domain.schemas import LoginRequest, RegisterRequest
from modules.accounts.repositories.account_password_repository import AccountPasswordRepository
from modules.accounts.repositories.account_repository import AccountRepository


class AccountAlreadyExistsError(CustomException):
    code = status.HTTP_409_CONFLICT
    message = "Account with this name already exists"


class InvalidCredentialsError(CustomException):
    code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid account name or password"


class AccountService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def register(self, request: RegisterRequest) -> Accounts:
        account_repo = self.uow.get_repository(AccountRepository)
        password_repo = self.uow.get_repository(AccountPasswordRepository)

        existing_accounts = await account_repo.filter(
            filter_conditions=[Accounts.account_name == request.account_name]
        )
        if existing_accounts:
            raise AccountAlreadyExistsError()

        account = await account_repo.create({"account_name": request.account_name})

        await password_repo.create(
            {
                "account_id": account.id,
                "hash_password": PasswordHandler.hash_password(request.password),
            }
        )

        return account

    async def login(self, request: LoginRequest) -> Accounts:
        account_repo = self.uow.get_repository(AccountRepository)
        password_repo = self.uow.get_repository(AccountPasswordRepository)

        accounts = await account_repo.filter(
            filter_conditions=[Accounts.account_name == request.account_name]
        )
        if not accounts:
            raise InvalidCredentialsError()

        account = accounts[0]
        password_records = await password_repo.filter(
            filter_conditions=[AccountPasswords.account_id == account.id]
        )
        if not password_records:
            raise InvalidCredentialsError()

        password_record = password_records[0]
        if not PasswordHandler.verify_password(request.password, password_record.hash_password):
            raise InvalidCredentialsError()

        return account
