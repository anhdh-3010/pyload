from enum import Enum
from functools import wraps

from core.database import async_session


class Propagation(Enum):
    REQUIRED = "required"
    REQUIRED_NEW = "required_new"


class Transactional:
    def __init__(self, propagation: Propagation = Propagation.REQUIRED):
        self.propagation = propagation

    def __call__(self, function):
        @wraps(function)
        async def decorator(*args, **kwargs):
            if self.propagation == Propagation.REQUIRED:
                return await self._run_required(function, args, kwargs)
            elif self.propagation == Propagation.REQUIRED_NEW:
                return await self._run_required_new(function, args, kwargs)
            else:
                return await self._run_required(function, args, kwargs)

        return decorator

    async def _run_required(self, function, args, kwargs):
        try:
            result = await function(*args, **kwargs)
            await async_session.commit()
            return result
        except Exception as e:
            await async_session.rollback()
            raise e

    async def _run_required_new(self, function, args, kwargs):
        try:
            async_session.begin()
            result = await function(*args, **kwargs)
            await async_session.commit()
            return result
        except Exception as e:
            await async_session.rollback()
            raise e
