# File: /src/app_logging.py

import logging
from logging.config import dictConfig
import os

# Ensure the logs directory exists
LOG_DIR = "/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Define the log file path
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Configure logging for the application
def configure_logging():
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "filename": LOG_FILE,
                    "formatter": "default",
                    "mode": "a",
                },
            },
            "root": {
                "level": "DEBUG",  # Set to 'DEBUG' for detailed logging in development
                "handlers": ["console", "file"],
            },
        }
    )


# Call this function to configure logging in the application
configure_logging()

# Re-export logging so other modules can use it like the built-in logging
getLogger = logging.getLogger
