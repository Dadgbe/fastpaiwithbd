import logging
import sys
from app.core.config import settings

def setup_logging():
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    # Отключаем лишние логи SQLAlchemy, если не DEBUG
    if not settings.DEBUG:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)