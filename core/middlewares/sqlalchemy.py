from starlette.types import ASGIApp, Receive, Scope, Send
from uuid6 import uuid7

from core.database.session import (
    async_session,
    reset_session_context,
    set_session_context,
)


class SQLAlchemyMiddleware:
    """
    Middleware to manage SQLAlchemy session lifecycle.

    Responsibilities:
    - Create scoped session per request via context var
    - Set up session context for dependency injection
    - Clean up session after request

    Note: Transaction management is delegated to UnitOfWork.
    Services should use UoW context manager for explicit transaction control.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        session_id = str(uuid7())
        context = set_session_context(session_id=session_id)

        try:
            await self.app(scope, receive, send)
        except Exception:
            raise
        finally:
            # Clean up session
            await async_session.remove()
            reset_session_context(context=context)
