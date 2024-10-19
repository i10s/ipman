# GraphQL resolvers for querying data
# File: /src/graphql_api/resolvers.py

from ariadne import QueryType
from graphql import GraphQLError
from sqlalchemy.orm import joinedload
import ipaddress
from database.models import IPAddress, Service
from database.db import get_db_session

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
        "rangeStart": str(ip.range_start) if ip.range_start else None,
        "rangeEnd": str(ip.range_end) if ip.range_end else None,
        "status": ip.status,
        "createdAt": ip.created_at,
        "updatedAt": ip.updated_at,
        "deactivatedAt": ip.deactivated_at,
        "service": service_to_dict(ip.service) if ip.service else None,
    }

# Resolver for fetching all services
def resolve_services(*_):
    with next(get_db_session()) as session:
        services = session.query(Service).all()
        return [service_to_dict(service) for service in services]

# Resolver for fetching all IP addresses
def resolve_ips(*_):
    with next(get_db_session()) as session:
        ips = session.query(IPAddress).options(joinedload(IPAddress.service)).all()
        return [ip_to_dict(ip) for ip in ips]

# Resolver for fetching an IP by address
def resolve_ip_by_address(_, info, address):
    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        raise GraphQLError(f"'{address}' is not a valid IP address.")

    with next(get_db_session()) as session:
        ip_record = session.query(IPAddress).filter(
            (IPAddress.ip_address == str(ip)) |
            (IPAddress.range_start <= str(ip)) & (IPAddress.range_end >= str(ip))
        ).options(joinedload(IPAddress.service)).first()

        if ip_record:
            if "service" in info.field_nodes[0].selection_set.selections:
                raise GraphQLError("Field 'service' must specify subfields like { id, name, description }.")
            return ip_to_dict(ip_record)
        else:
            return None  # If no IP record is found, return None

query.set_field("ipAddresses", resolve_ips)
query.set_field("ipByAddress", resolve_ip_by_address)
