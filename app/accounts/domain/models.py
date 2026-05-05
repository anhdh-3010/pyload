from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid

from core import Base


class Accounts(Base):
    __tablename__ = "accounts"

    account_name: Mapped[str] = mapped_column(String(256), nullable=False, unique=True, index=True)


class AccountPasswords(Base):
    __tablename__ = "account_passwords"

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )
    hash_password: Mapped[str] = mapped_column(String(512), nullable=False)
