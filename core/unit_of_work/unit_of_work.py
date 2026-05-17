import logging
from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession

from core.repository.base import BaseRepository
from core.unit_of_work.abs import AbstractUnitOfWork

logger = logging.getLogger(__name__)


class UnitOfWork(AbstractUnitOfWork):
    """
    Concrete Unit of Work implementation.

    Manages repositories, transactions, and provides access to the session.

    Features:
    - Repository caching (identity map)
    - Transaction management (begin/commit/rollback)
    - Async context manager support
    - Automatic cleanup on context exit
    """

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
        self._repositories: dict[str, BaseRepository] = {}

    async def __aenter__(self):
        """Begin transaction on context entry."""
        await self.session.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Handle transaction exit and cleanup."""
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        """Commit all changes to database."""
        try:
            await self.session.commit()
        except Exception as e:
            logger.exception(f"Failed to commit unit of work; rolling back transaction: {e}")
            await self.rollback()
            raise

    async def rollback(self) -> None:
        """Rollback all changes."""
        await self.session.rollback()

    def get_repository[RepositoryType: BaseRepository](
        self,
        repository_type: type[RepositoryType],
    ) -> RepositoryType:
        """
        Get or create repository for given class.
        Caches repositories to ensure identity map consistency
        and repository reuse within transaction scope.

        :param repository_type: Repository class
        :return: Repository instance for the class
        """
        repository_name = repository_type.__name__

        if repository_name not in self._repositories:
            self._repositories[repository_name] = repository_type(self.session)

        return cast(RepositoryType, self._repositories[repository_name])
