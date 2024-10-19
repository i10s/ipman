# File: /src/app.py

from flask import Flask, request, jsonify
from ariadne import graphql_sync
from ariadne.constants import PLAYGROUND_HTML
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
from database.db import get_db_session
from graphql_api.schema import schema  # Correct import from the graphql_api folder

# Initialize the Flask app
app = Flask(__name__)


# Health check endpoint with database check
@app.route("/health", methods=["GET"])
def health_check():
    try:
        # Try a simple query to check database connectivity
        db_session = next(get_db_session())  # Get a database session
        result = db_session.execute(
            text("SELECT 1")
        ).fetchone()  # Use text() for raw SQL
        if result:
            return jsonify({"status": "healthy", "database": "connected"}), 200
    except OperationalError:
        # If the database connection fails, return an unhealthy status
        return jsonify({"status": "unhealthy", "database": "connection failed"}), 500
    except Exception as e:
        # Catch any other issues in the health check
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


# Serve the GraphQL playground and API
@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=True)
    status_code = 200 if success else 400
    return jsonify(result), status_code


# Main entry point to run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
