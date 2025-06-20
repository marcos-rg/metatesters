import logging
import os

def setup_logging():
    # Get log level from environment variable (default to INFO)
    log_level = os.getenv("PYTHON_LOG_LEVEL", "INFO").upper()

    logging.basicConfig(level=getattr(logging, log_level, logging.INFO),
                        format="%(asctime)s - %(levelname)s - %(message)s")