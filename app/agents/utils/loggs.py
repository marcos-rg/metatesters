import logging
from app.config.config import settings

def setup_logging():
    # Get log level from environment variable (default to INFO)
    log_level = settings.python_log_level.upper()

    logging.basicConfig(level=getattr(logging, log_level, logging.INFO),
                        format="%(asctime)s - %(levelname)s - %(message)s")