"""
Core module exports - Import commonly used classes/functions here
"""

# Security
from core.security import JWTHandler, oauth

# Config
from core.config import config

# Database
from core.database.session import get_async_session, Base
from core.database.transactional import Transactional

# Repository
from core.repository import BaseRepository

# Exceptions
from core.exceptions import (
    CustomException,
    BadRequestException,
    UnauthorizedException,
    NotFoundException,
)

__all__ = [
    # Security
    "JWTHandler",
    "oauth",
    # Config
    "config",
    # Database
    "get_async_session",
    "Base",
    "Transactional",
    # Repository
    "BaseRepository",
    # Exceptions
    "CustomException",
    "BadRequestException",
    "UnauthorizedException",
    "NotFoundException",
]
