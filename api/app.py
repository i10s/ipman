# File: app.py

import threading
import os
import comm.app_logging as logging
from logging.config import dictConfig
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from ariadne import graphql_sync
from ariadne.constants import PLAYGROUND_HTML
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload
from sqlalchemy.dialects.postgresql import CIDR
from database.db import get_db_session
from database.models import IPAddress, Service # Import the IPAddress model and  the Service model here
from api.schema import schema
from graphql import GraphQLError


# Initialize the Flask app for the API
api_app = Flask(__name__)

# Custom error formatter to simplify the error output
def custom_format_error(error, debug):
    if isinstance(error, GraphQLError):
        return {"message": error.message, "path": error.path}
    # Default formatting for other exceptions
    return {"message": str(error), "debug": debug}  # You can choose to log this or not


# Configure logging for both API and Web applications
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
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
        },
        "root": {
            "level": "INFO",  # Use 'DEBUG' for more detailed logs in development
            "handlers": ["wsgi"],
        },
    }
)

logger = logging.getLogger(__name__)


# Health check for the API
@api_app.route("/health", methods=["GET"])
def health_check():
    try:
        # Test database connectivity
        db_session = next(get_db_session())
        result = db_session.execute(text("SELECT 1")).fetchone()  # Basic DB query
        if result:
            logger.info("API Health check passed, database connected.")
            return jsonify({"status": "healthy", "database": "connected"}), 200
    except OperationalError:
        logger.error("Database connection failed during API health check.")
        return jsonify({"status": "unhealthy", "database": "connection failed"}), 500
    except Exception as e:
        logger.error(f"API Health check error: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


# GraphQL Playground at /graphql
@api_app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML  # Use the constant for the GraphQL Playground


# GraphQL execution endpoint
@api_app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    logger.info(f"GraphQL request received: {data}")
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=True,
        error_formatter=custom_format_error,
    )
    if success:
        logger.info("GraphQL query executed successfully.")
    else:
        logger.error("GraphQL query execution failed.")
    return jsonify(result)


# Route to fetch and display services and IPs for the API
@api_app.route("/", methods=["GET"])
def index():
    with next(get_db_session()) as session:
        # Query all services and IPs
        services = session.query(Service).all()
        ips = session.query(IPAddress).options(joinedload(IPAddress.service)).all()

        # Pass both services and IPs to the template (if needed)
        return render_template("index.html", services=services, ips=ips)


# Function to run API (on all IPs)
def run_api():
    api_app.run(debug=True, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    run_api()  # Simply run the API without threading


