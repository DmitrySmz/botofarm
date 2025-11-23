import uvicorn

from app.app_object import create_app
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting server at {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
    )
