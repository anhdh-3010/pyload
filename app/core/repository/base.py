from typing import Any, Generic, List, Optional, Type, TypeVar, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import Base
from app.core.exceptions.base import NotFoundException


from app.core.repository.abs import AbsRepository


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(AbsRepository, Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db_session: AsyncSession) -> None:
        self.session = db_session
        self.model_class: Type[ModelType] = model

    async def create(self, entity: dict[str, Any]) -> ModelType:
        if entity is None:
            entity = {}
        model = self.model_class(**entity)
        self.session.add(model)
        await self.session.flush()
        return model

    async def get_all(self) -> Sequence[ModelType]:
        """Get all entities from the repository."""
        stmt = select(self.model_class)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, entity_id: Any) -> ModelType | None:
        """Get an entity by its ID."""
        return await self.session.get(self.model_class, entity_id)

    async def delete(self, entity_id: Any) -> bool:
        """Delete an entity by its ID."""
        entity = await self.get_by_id(entity_id)
        if not entity:
            raise NotFoundException(
                f"{self.model_class.__tablename__.title()} with id: {id} does not exist"
            )

        await self.session.delete(entity)
        await self.session.flush()
        return True

    async def update(self, entity_id: Any, entity: dict[str, Any]) -> ModelType | None:
        """Update an entity by its ID."""
        db_entity = await self.get_by_id(entity_id)
        if not entity:
            raise NotFoundException(
                f"{self.model_class.__tablename__.title()} with id: {id} does not exist"
            )

        for key, value in entity.items():
            if hasattr(db_entity, key):
                setattr(db_entity, key, value)

        await self.session.flush()
        return db_entity

    async def filter(
        self,
        filter_conditions: Optional[List] = None,
        joins: Optional[List] = None,
        options: Optional[List] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Sequence[ModelType] | None:
        query = select(self.model_class)

        if joins:
            for join_model, on_condition in joins:
                query = query.join(join_model, on_condition)

        if filter_conditions:
            for condition in filter_conditions:
                query = query.where(condition)

        if options:
            for option in options:
                query = query.options(option)

        if limit is not None:
            query = query.limit(limit)

        if offset is not None:
            query = query.offset(offset)

        result = await self.session.execute(query)
        return result.scalars().all()
