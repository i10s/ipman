# GraphQL schema and queries definitions
# File: schema.py

from ariadne import QueryType, make_executable_schema
from api.resolvers import resolve_services, resolve_ips, resolve_ip_by_address

# Define the Query type
query = QueryType()

# Define resolvers for the queries
query.set_field("services", resolve_services)
query.set_field("ipAddresses", resolve_ips)
query.set_field("ipByAddress", resolve_ip_by_address)

# The GraphQL schema, only defining Queries, no Mutations (read-only)
type_defs = """
    type Service {
        id: ID!
        name: String!
        description: String
        ipAddresses: [IPAddress!]!  
    }

    type IPAddress {
        id: ID!
        ipAddress: String
        ipRange: String  
        rangeStart: String
        rangeEnd: String
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
        ipByAddress(address: String!): IPAddress
        ipByCIDR(cidr: String!): [IPAddress]
    }


    """


# Create executable schema
schema = make_executable_schema(type_defs, query)
