from abc import ABC, abstractmethod
from typing import Any


class AbsRepository(ABC):
    @abstractmethod
    async def create(self, entity: dict[str, Any]) -> Any:
        """Add an entity to the repository."""
        pass

    @abstractmethod
    async def get_all(self) -> Any:
        """List all entities in the repository."""
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: Any) -> Any:
        """Retrieve an entity by its ID."""
        pass

    @abstractmethod
    async def delete(self, entity_id: Any) -> Any:
        """Remove an entity by its ID."""
        pass

    @abstractmethod
    async def update(self, entity_id: Any, entity: dict[str, Any]) -> Any | None:
        """Update an entity by its ID."""
        pass
