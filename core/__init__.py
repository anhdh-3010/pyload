"""
Core module exports - Import commonly used classes/functions here
"""

# Security
# Config
from core.config import config

# Database
from core.database.session import Base, get_async_db_session, get_unit_of_work

# Exceptions
from core.exceptions import (
    BadRequestException,
    CustomException,
    NotFoundException,
    UnauthorizedException,
)

# Repository
from core.repository.base import BaseRepository
from core.security import JWTHandler

# Unit of Work
from core.unit_of_work import UnitOfWork

__all__ = [
    # Security
    "JWTHandler",
    # Config
    "config",
    # Database
    "get_unit_of_work",
    "get_async_db_session",
    "Base",
    # Unit of Work
    "UnitOfWork",
    # Repository
    "BaseRepository",
    # Exceptions
    "CustomException",
    "BadRequestException",
    "UnauthorizedException",
    "NotFoundException",
]
