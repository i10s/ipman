# File: schema.py
from ariadne import QueryType, make_executable_schema, ScalarType
from graphql import GraphQLError
from api.resolvers import (
    resolve_services, 
    resolve_service, 
    resolve_ips, 
    resolve_ip_by_address, 
    resolve_ip_by_cidr
)

import ipaddress

# Scalar for IPAddress renamed to avoid conflict
ip_scalar = ScalarType("IPAddressScalar")
cidr_scalar = ScalarType("CIDR")

# Define serializer and parser for IPAddress scalar
@ip_scalar.serializer
def serialize_ip(value):
    return str(value)

@ip_scalar.value_parser
def parse_ip(value):
    try:
        # Attempt to parse the value as an IP address
        return str(ipaddress.ip_address(value))
    except ValueError:
        # Raise a cleaner error message
        raise GraphQLError(f"The provided IP address '{value}' is invalid. Please ensure it is a valid IPv4 or IPv6 address.")


# Define serializer and parser for CIDR scalar
@cidr_scalar.serializer
def serialize_cidr(value):
    return str(value)

@cidr_scalar.value_parser
def parse_cidr(value):
    try:
        return str(ipaddress.ip_network(value, strict=False))
    except ValueError:
        raise ValueError(f"Invalid CIDR block: {value}")

# Define the Query type
query = QueryType()

# Set up resolvers for the queries
query.set_field("services", resolve_services)
query.set_field("service", resolve_service)  # For querying a specific service
query.set_field("ipAddresses", resolve_ips)
query.set_field("ipByAddress", resolve_ip_by_address)
query.set_field("ipByCIDR", resolve_ip_by_cidr)

# Updated GraphQL schema definition
type_defs = """
scalar CIDR
scalar IPAddressScalar  
type Service {
    id: ID!
    name: String!
    description: String
    createdAt: String
    ipAddresses: [IPAddress!]! 
}

type IPAddress {
    id: ID!
    ipAddress: IPAddressScalar  
    ipRange: CIDR        
    rangeStart: IPAddressScalar
    rangeEnd: IPAddressScalar   
    status: String!
    createdAt: String
    updatedAt: String
    deactivatedAt: String
    service: Service
}

type Query {
    services: [Service!]!
    service(id: ID!): Service  
    ipAddresses: [IPAddress!]!
    ipByAddress(address: IPAddressScalar!): IPAddress 
    ipByCIDR(cidr: CIDR!): [IPAddress!]  
}
"""

# Create executable schema
schema = make_executable_schema(type_defs, query, ip_scalar, cidr_scalar)
