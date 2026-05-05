from abc import ABC, abstractmethod


class AbstractUnitOfWork(ABC):
    """
    Abstract Unit of Work interface.

    Defines contract for managing repositories and transactions within a request scope.
    """

    @abstractmethod
    async def __aenter__(self):
        """Enter async context manager."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commit all changes to the database."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback all changes."""
        pass

    @abstractmethod
    def get_repository(self, model):
        """Get repository for given model."""
        pass
