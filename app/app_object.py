from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.db.database import Base, engine
from app.middlewares.auth_logging import AuthLoggingMiddleware
from app.middlewares.corse import setup_cors
from app.routes import root_router
from app.utils.logger import get_logger

logger = get_logger("validation")


async def _create_tables() -> None:
    from app.db.models import user

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.api_title)

    app.add_middleware(AuthLoggingMiddleware)
    setup_cors(app)

    app.include_router(root_router)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        logger.warning(
            "Validation error at %s %s: %s",
            request.method,
            request.url.path,
            exc.errors(),
        )
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    @app.on_event("startup")
    async def on_startup() -> None:
        await _create_tables()

    return app
