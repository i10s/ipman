# File: /src/logging.py

import logging  # Import Python's built-in logging module
from logging.config import dictConfig

# Configure logging for the application
def configure_logging():
    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            },
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'default',
            },
        },
        'root': {
            'level': 'INFO',  # Change to 'DEBUG' for more detailed logging in development
            'handlers': ['wsgi'],
        },
    })

# Call this function in the app to configure logging
configure_logging()

# Re-export logging so other modules can use it like the built-in logging
getLogger = logging.getLogger  # Ensure this refers to the built-in logging.getLogger
