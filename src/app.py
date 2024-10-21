# File: /src/app.py

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import app_logging as logging
from logging.config import dictConfig
from ariadne import graphql_sync
from ariadne.constants import PLAYGROUND_HTML
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload
from sqlalchemy.dialects.postgresql import CIDR
from database.db import get_db_session
from database.models import IPAddress  # Import the IPAddress model here
from database.models import Service  # Import the Service model
from graphql_api.schema import schema  # Correct import from the graphql_api folder
from graphql import GraphQLError
import threading
import os


# Initialize the Flask app for the API
api_app = Flask(__name__)

# Initialize another Flask app for the Web Interface
web_app = Flask(__name__, static_folder="static", template_folder="templates")

# Set the secret key to some random bytes. Keep this secret and unique in a real application.
web_app.secret_key = os.urandom(24)


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


# Route to show service creation form (or edit if id is provided)
@web_app.route("/add-service", methods=["GET"])
def add_service_form():
    service_id = request.args.get("id")  # Get the service ID from the query parameters
    if service_id:
        with next(get_db_session()) as session:
            service = session.query(Service).get(
                service_id
            )  # Fetch service by ID if provided
            if service:
                return render_template(
                    "service_form.html", service=service
                )  # Pass service to the template
    # If no service ID is provided, render an empty form for adding a new service
    return render_template("service_form.html", service=None)


# Route to list all services
@web_app.route("/services", methods=["GET"])
def service_list():
    with next(get_db_session()) as session:
        services = session.query(Service).all()
        return render_template("service_list.html", services=services)


# Route to handle form submission for adding/updating a service
@web_app.route("/service/save", methods=["POST"])
def save_service():
    service_name = request.form.get("service_name")
    service_description = request.form.get(
        "service_description"
    )  # Include description field
    service_id = request.args.get(
        "id"
    )  # Retrieve the 'id' from URL parameters (not form data)

    # Ensure that the service name is provided
    if not service_name:
        flash("Service name is required.")
        return redirect(request.referrer)

    with next(get_db_session()) as session:
        if service_id:  # If 'id' is present in URL, update the existing record
            service = session.query(Service).get(service_id)
            if not service:
                flash("Service not found.")
                return redirect(request.referrer)

            # Update existing service fields
            service.name = service_name
            service.description = service_description  # Update description if provided
        else:  # No 'id' means this is a new record
            new_service = Service(
                name=service_name,
                description=service_description,  # Set description
                created_at=func.now(),
            )
            session.add(new_service)

        session.commit()

    return redirect(url_for("service_list"))


# Route to edit a service
@web_app.route("/edit-service/<int:id>", methods=["GET"])
def edit_service(id):
    with next(get_db_session()) as session:
        service = session.query(Service).get(id)
        return render_template("service_form.html", service=service)


# Route to edit an IP
@web_app.route("/edit-ip/<int:id>", methods=["GET"])
def edit_ip(id):
    with next(get_db_session()) as session:
        ip = session.query(IPAddress).get(id)
        if not ip:
            flash("IP not found.")
            return redirect(url_for("ip_list"))
        services = session.query(Service).all()  # Fetch all services
        return render_template("ip_form.html", ip=ip, services=services)


# Route to delete a service
@web_app.route("/delete-service/<int:service_id>", methods=["GET"])
def delete_service(service_id):
    with next(get_db_session()) as session:
        service = session.query(Service).get(service_id)
        if service:
            session.delete(service)
            session.commit()
    return redirect(url_for("service_list"))


# Route to show IP creation/update form
@web_app.route("/ip", methods=["GET"])
def ip_form():
    ip_id = request.args.get("id")

    with next(get_db_session()) as session:
        services = session.query(Service).all()  # Fetch all services

        if ip_id:
            ip = session.query(IPAddress).get(ip_id)
            return render_template(
                "ip_form.html", action="Update", ip=ip, services=services
            )

        return render_template(
            "ip_form.html", action="Create", ip=None, services=services
        )


from ipaddress import ip_network

# Route to handle form submission for adding or updating an IP
@web_app.route("/ip/save", methods=["POST"])
def save_ip():
    ip_address = request.form.get("ipAddress")
    ip_range = request.form.get("ip_range")
    range_start = request.form.get("range_start")
    range_end = request.form.get("range_end")
    service_id = request.form.get("service_id")
    status = request.form.get("status")

    # Ensure that the service_id and status are provided
    if not service_id or not status:
        flash("Service and status are required.")
        return redirect(request.referrer)

    # Ensure that at least an IP address, an IP range, or both range start and end are provided
    if not ip_address and not ip_range and (not range_start or not range_end):
        flash(
            "Please provide either an IP address, an IP range, or a valid start and end range."
        )
        return redirect(request.referrer)

    # Convert empty fields to None instead of empty strings
    if not ip_address:
        ip_address = None
    if not ip_range:
        ip_range = None
    if not range_start:
        range_start = None
    if not range_end:
        range_end = None

    # Validate and correct the CIDR range if provided
    if ip_range:
        try:
            ip_range = str(ip_network(ip_range, strict=False))  # Auto-corrects the CIDR block
        except ValueError:
            flash("Invalid CIDR range. Please provide a valid network address.")
            return redirect(request.referrer)

    with next(get_db_session()) as session:
        if "id" in request.args:  # If updating an existing IP
            ip = session.query(IPAddress).get(request.args["id"])
            if not ip:
                flash("IP not found.")
                return redirect(request.referrer)

            # Update existing record
            ip.ip_address = ip_address
            ip.ip_range = ip_range
            ip.range_start = range_start
            ip.range_end = range_end
            ip.service_id = service_id
            ip.status = status
            ip.updated_at = func.now()

        else:  # If adding a new IP or range
            new_ip = IPAddress(
                ip_address=ip_address,
                ip_range=ip_range,
                range_start=range_start,
                range_end=range_end,
                service_id=service_id,
                status=status,
                created_at=func.now(),
                updated_at=func.now(),
            )
            session.add(new_ip)
        session.commit()

    return redirect(url_for("ip_list"))


# Route to list all IPs (for viewing in a list)
@web_app.route("/ips", methods=["GET"])
def ip_list():
    with next(get_db_session()) as session:
        ips = (
            session.query(IPAddress).options(joinedload(IPAddress.service)).all()
        )  # Ensure service is fetched
        return render_template("ip_list.html", ips=ips)


# Route to show IP creation/update form
@web_app.route("/add-ip", methods=["GET"])
def add_ip_form():
    with next(get_db_session()) as session:
        services = session.query(Service).all()  # Fetch all services from the database
    return render_template(
        "ip_form.html", services=services
    )  # Pass services to the template


from ipaddress import ip_network

# Route to handle form submission for adding an IP or Range
@web_app.route("/add-ip", methods=["POST"])
def add_ip():
    ip_address = request.form.get("ipAddress")
    ip_range = request.form.get("ip_range")
    range_start = request.form.get("range_start")
    range_end = request.form.get("range_end")
    service_id = request.form.get("service_id")
    status = request.form.get("status")

    # Ensure that at least one of IP, range, or CIDR is provided
    if not ip_address and not ip_range and (not range_start or not range_end):
        flash("Please provide either an IP address, a valid IP range, or a CIDR.")
        return redirect(url_for("add_ip_form"))

    # Convert empty fields to None instead of empty strings
    if not ip_address:
        ip_address = None
    if not ip_range:
        ip_range = None
    if not range_start:
        range_start = None
    if not range_end:
        range_end = None

    # Validate and correct the CIDR range if provided
    if ip_range:
        try:
            ip_range = str(ip_network(ip_range, strict=False))  # Auto-corrects the CIDR block
        except ValueError:
            flash("Invalid CIDR range. Please provide a valid network address.")
            return redirect(url_for("add_ip_form"))

    with next(get_db_session()) as session:
        # Create a new IP or range
        ip = IPAddress(
            ip_address=ip_address,  # If no IP is provided, it's None
            ip_range=ip_range,  # CIDR notation, auto-corrected
            range_start=range_start,  # Handle empty range_start as None
            range_end=range_end,  # Handle empty range_end as None
            service_id=service_id,
            status=status,
            created_at=func.now(),  # Set created_at timestamp
            updated_at=func.now(),  # Set updated_at timestamp
        )
        session.add(ip)
        session.commit()

    return redirect(url_for("index"))



# Route to activate/deactivate an IP
@web_app.route("/ip/toggle/<int:ip_id>", methods=["GET"])
def toggle_ip_status(ip_id):
    with next(get_db_session()) as session:
        ip = session.query(IPAddress).get(ip_id)
        if ip.status == "active":
            ip.deactivate()
        else:
            ip.activate()
        session.commit()
    return redirect(url_for("ip_list"))


# GraphQL Playground at /graphql
@api_app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML  # Use the constant for the GraphQL Playground


# GraphQL execution endpoint
@api_app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=False,
        error_formatter=custom_format_error,
    )
    if success:
        logger.info("GraphQL query executed successfully.")
    else:
        logger.error("GraphQL query execution failed.")
    return jsonify(result)


# Serve the web app, restricted to the internal IP (e.g., 10.0.0.1)
@web_app.route("/", methods=["GET"])
def index():
    with next(get_db_session()) as session:
        # Query all services and IPs
        services = session.query(Service).all()
        ips = session.query(IPAddress).options(joinedload(IPAddress.service)).all()

        # Pass both services and IPs to the template
        return render_template("index.html", services=services, ips=ips)


# Function to run API (on all IPs)
def run_api():
    api_app.run(host="0.0.0.0", port=5000)


# Function to run Web App (on internal IP only)
def run_web():
    web_app.run(
        host="0.0.0.0", port=5001
    )  # Replace 10.0.0.1 with your internal/private IP


# Running both API and Web App in separate threads
if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api)
    web_thread = threading.Thread(target=run_web)

    # Start both threads
    api_thread.start()
    web_thread.start()

    # Join threads to keep both servers running
    api_thread.join()
    web_thread.join()
