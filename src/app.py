# File: /src/app.py

from flask import Flask, request, jsonify
import app_logging as logging
from logging.config import dictConfig
from ariadne import graphql_sync
from ariadne.constants import PLAYGROUND_HTML
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
from database.db import get_db_session
from graphql_api.schema import schema  # Correct import from the graphql_api folder
from graphql import GraphQLError

# Initialize the Flask app
app = Flask(__name__)

# Custom error formatter to simplify the error output
def custom_format_error(error, debug):
    if isinstance(error, GraphQLError):
        return {
            "message": error.message,
            "path": error.path
        }
    # Default formatting for other exceptions
    return {
        "message": str(error)
    }

# Configure logging for the application
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

logger = logging.getLogger(__name__)  # Create a logger for this module

# Health check endpoint with database check
@app.route("/health", methods=["GET"])
def health_check():
    try:
        # Try a simple query to check database connectivity
        db_session = next(get_db_session())  # Get a database session
        result = db_session.execute(text("SELECT 1")).fetchone()  # Use text() for raw SQL
        if result:
            logger.info("Health check passed")
            return jsonify({"status": "healthy", "database": "connected"}), 200
    except OperationalError:
        logger.error("Database connection failed during health check")
        return jsonify({"status": "unhealthy", "database": "connection failed"}), 500
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# Serve GraphQL Playground at /graphql
@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML  # Use the constant for the GraphQL Playground

# GraphQL execution endpoint
@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=False, error_formatter=custom_format_error)
    logger.info("GraphQL query executed successfully")
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
