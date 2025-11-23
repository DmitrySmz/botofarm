from fastapi import APIRouter

from app.config.settings import settings
from app.endpoints.healthcheck import router as health_router
from app.endpoints.users import router as users_router


root_router = APIRouter(
    prefix=settings.API_PREFIX,
)

root_router.include_router(health_router)
root_router.include_router(users_router)
