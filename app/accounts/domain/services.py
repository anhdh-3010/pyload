from fastapi import status

from app.accounts.domain.models import AccountPasswords, Accounts
from app.accounts.domain.schemas import LoginRequest, RegisterRequest
from core import UnitOfWork
from core.exceptions import CustomException
from core.security.password import PasswordHandler


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
        """Register a new account."""
        account_repo = self.uow.get_repository(Accounts)
        password_repo = self.uow.get_repository(AccountPasswords)

        # Check if account already exists
        existing_accounts = await account_repo.filter(
            filter_conditions=[Accounts.account_name == request.account_name]
        )

        if existing_accounts:
            raise AccountAlreadyExistsError()

        # Create new account
        account_data = {
            "account_name": request.account_name,
        }
        account = await account_repo.create(account_data)

        # Hash password and create password record
        hashed_password = PasswordHandler.hash_password(request.password)
        password_data = {
            "account_id": account.id,
            "hash_password": hashed_password,
        }
        await password_repo.create(password_data)

        return account

    async def login(self, request: LoginRequest) -> Accounts:
        """Authenticate account and return account object if successful."""
        account_repo = self.uow.get_repository(Accounts)
        password_repo = self.uow.get_repository(AccountPasswords)

        # Find account by account_name
        accounts = await account_repo.filter(
            filter_conditions=[Accounts.account_name == request.account_name]
        )

        if not accounts:
            raise InvalidCredentialsError()

        account = accounts[0]

        # Find password record for this account
        password_records = await password_repo.filter(
            filter_conditions=[AccountPasswords.account_id == account.id]
        )

        if not password_records:
            raise InvalidCredentialsError()

        password_record = password_records[0]

        # Verify password
        if not PasswordHandler.verify_password(request.password, password_record.hash_password):
            raise InvalidCredentialsError()

        return account
