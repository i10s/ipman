# File: /src/graphql_api/resolvers.py

from ariadne import QueryType
from graphql import GraphQLError
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func
import ipaddress
from ipaddress import ip_network
from database.models import IPAddress, Service
from database.db import get_db_session
import app_logging as logging

# Initialize a query type for GraphQL queries
query = QueryType()


# Helper function to convert Service model to dictionary
def service_to_dict(service):
    return {
        "id": service.id,
        "name": service.name,
        "description": service.description,
    }


# Helper function to convert IPAddress model to dictionary
def ip_to_dict(ip):
    return {
        "id": ip.id,
        "ipAddress": str(ip.ip_address) if ip.ip_address else None,
        "ip_range": str(ip.ip_range) if ip.ip_range else None,
        "rangeStart": str(ip.range_start) if ip.range_start else None,
        "rangeEnd": str(ip.range_end) if ip.range_end else None,
        "status": ip.status,
        "createdAt": ip.created_at,
        "updatedAt": ip.updated_at,
        "deactivatedAt": ip.deactivated_at,
        "service": service_to_dict(ip.service) if ip.service else None,
    }


# Validator for IP address and range
def validate_ip_and_range(ip_address, range_start, range_end):
    if not ip_address and not (range_start and range_end):
        raise GraphQLError(
            "You must provide either a single IP address or a valid range (start and end)."
        )
    if ip_address:
        try:
            ip = ipaddress.ip_address(ip_address)
        except ValueError:
            raise GraphQLError(f"'{ip_address}' is not a valid IP address.")
    if range_start and range_end:
        try:
            start_ip = ipaddress.ip_address(range_start)
            end_ip = ipaddress.ip_address(range_end)
            if start_ip > end_ip:
                raise GraphQLError("Range start cannot be greater than range end.")
        except ValueError:
            raise GraphQLError(
                f"'{range_start}' or '{range_end}' is not a valid IP address."
            )



# Resolver for fetching all services
def resolve_services(*_):
    logger = logging.getLogger(__name__)
    try:
        with next(get_db_session()) as session:
            services = session.query(Service).all()
            logger.info("Successfully fetched all services.")
            return [service_to_dict(service) for service in services]
    except Exception as e:
        logger.error(f"Failed to fetch services: {e}")
        raise GraphQLError("Error fetching services.")


# Resolver for IPAddress based on CIDR
def resolve_ip_by_cidr(_, info, cidr):
    with next(get_db_session()) as session:
        # Validate and parse CIDR input
        try:
            cidr_network = str(ip_network(cidr, strict=False))  # Parse CIDR network
        except ValueError:
            raise ValueError("Invalid CIDR format")

        # Query the database for IP addresses within this CIDR block
        ips = session.query(IPAddress).filter(
            func.text(f"'{cidr_network}'::cidr").op(">>")(IPAddress.ip_range)
        ).all()

        return ips  # Return matching IP addresses


# Resolver for fetching all IP addresses
def resolve_ips(*_):
    logger = logging.getLogger(__name__)
    try:
        with next(get_db_session()) as session:
            ips = session.query(IPAddress).options(joinedload(IPAddress.service)).all()
            logger.info("Successfully fetched all IP addresses.")
            return [ip_to_dict(ip) for ip in ips]
    except Exception as e:
        logger.error(f"Failed to fetch IP addresses: {e}")
        raise GraphQLError("Error fetching IP addresses.")


# Resolver for fetching an IP by address
def resolve_ip_by_address(_, info, address):
    logger = logging.getLogger(__name__)  # Create a logger for this module

    try:
        # Validate the IP address
        ip = ipaddress.ip_address(address)
    except ValueError:
        # Log the error using the new logging system
        logger.error(f"Invalid IP address input: {address}")
        # Return a clean GraphQL error to the client without logging it twice
        raise GraphQLError(f"'{address}' is not a valid IP address.")

    with next(get_db_session()) as session:
        # Query to find IP by either single IP or range
        ip_record = (
            session.query(IPAddress)
            .filter(
                (IPAddress.ip_address == str(ip))
                | (
                    (IPAddress.range_start <= str(ip))
                    & (IPAddress.range_end >= str(ip))
                )
            )
            .options(joinedload(IPAddress.service))
            .first()
        )

        if ip_record:
            # Check if the client is requesting the "service" field without specifying subfields
            selections = [
                field.name.value
                for field in info.field_nodes[0].selection_set.selections
            ]
            if (
                "service" in selections
                and "id" not in selections
                and "name" not in selections
            ):
                logger.warning(f"Field 'service' missing subfields for IP: {address}")
                raise GraphQLError(
                    "Field 'service' must specify subfields like { id, name, description }."
                )
            return ip_to_dict(ip_record)
        else:
            logger.info(f"No IP record found for address: {address}")
            return None  # If no IP record is found, return None


# Resolver to fetch a specific service by ID
def resolve_service(_, info, id):
    with next(get_db_session()) as session:
        service = session.query(Service).get(int(id)) 
        if service:
            return service
        raise ValueError("Service not found")



# Set the fields for the GraphQL queries
query.set_field("services", resolve_services)
query.set_field("ipAddresses", resolve_ips)
query.set_field("ipByAddress", resolve_ip_by_address)
query.set_field("ipByCIDR", resolve_ip_by_cidr)
query.set_field("service", resolve_service)

