# type: ignore[arg-type]
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.accounts.routers import private_router as private_accounts_router
from app.api.v1.accounts.routers import router as accounts_router
from app.api.v1.download_tasks.routers import (
    private_router as private_download_tasks_router,
)
from core import CustomException, config
from core.middlewares import (
    ResponseLoggerMiddleware,
    SQLAlchemyMiddleware,
)


def init_listeners(app_: FastAPI) -> None:
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )


def init_routers(app_: FastAPI) -> None:
    app_.include_router(accounts_router, prefix="/api/v1", tags=["auth"])
    app_.include_router(private_accounts_router, prefix="/api/v1", tags=["accounts"])
    app_.include_router(
        private_download_tasks_router,
        prefix="/api/v1",
        tags=["download_tasks"],
    )


def make_middleware() -> list[Middleware]:
    middleware = [
        Middleware(
            SessionMiddleware,
            secret_key=config.session_secret_key or config.jwt_secret_key,
            session_cookie="oauth_session",
            max_age=1800,  # 30 minutes
            same_site="lax",
            https_only=False,  # Set to True in production with HTTPS
            path="/",
        ),
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(SQLAlchemyMiddleware),
        Middleware(ResponseLoggerMiddleware),
    ]
    return middleware


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="FastAPI Boilerplate",
        description="FastAPI Boilerplate by @iam-abbas",
        version="1.0.0",
        docs_url=None if config.environment == "production" else "/docs",
        redoc_url=None if config.environment == "production" else "/redoc",
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    init_listeners(app_=app_)
    return app_


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host=config.app_host, port=config.app_port)
