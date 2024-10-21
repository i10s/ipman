
# API Documentation

## Overview

This document provides detailed information on how to interact with the GraphQL API for managing IP addresses and services. You will find query examples, input parameter explanations, and descriptions of returned data.

## Endpoint

- **GraphQL API URL**: `/graphql`
- The API is read-only, and mutations are not allowed.

## Queries

### 1. Fetch All Services

Fetch all available services.

**Query Example**:

```graphql
{
  services {
    id
    name
    description
  }
}
```

**Response Example**:

```json
{
  "data": {
    "services": [
      {
        "id": "1",
        "name": "ChannelX",
        "description": "IP addresses for ChannelX services"
      },
      {
        "id": "2",
        "name": "Sellers",
        "description": "IP addresses for seller connections"
      }
    ]
  }
}
```

### 2. Fetch All IP Addresses

Fetch all individual IP addresses and IP ranges with their associated services.

**Query Example**:

```graphql
{
  ipAddresses {
    id
    ipAddress
    rangeStart
    rangeEnd
    status
    createdAt
    updatedAt
    deactivatedAt
    service {
      id
      name
      description
    }
  }
}
```

**Response Example**:

```json
{
  "data": {
    "ipAddresses": [
      {
        "id": "1",
        "ipAddress": "185.180.14.1",
        "rangeStart": null,
        "rangeEnd": null,
        "status": "active",
        "createdAt": "2024-10-15T12:30:45",
        "updatedAt": "2024-10-16T10:20:11",
        "deactivatedAt": null,
        "service": {
          "id": "1",
          "name": "ChannelX",
          "description": "IP addresses for ChannelX services"
        }
      },
      {
        "id": "33",
        "ipAddress": null,
        "rangeStart": "185.180.14.0",
        "rangeEnd": "185.180.14.255",
        "status": "active",
        "createdAt": "2024-10-10T09:15:00",
        "updatedAt": null,
        "deactivatedAt": null,
        "service": {
          "id": "2",
          "name": "Sellers",
          "description": "IP addresses for seller connections"
        }
      }
    ]
  }
}
```

### 3. Fetch IP Address by Specific Address

Fetch details of a specific IP address or check if an IP falls within a defined range.

**Query Example**:

```graphql
{
  ipByAddress(address: "185.180.14.10") {
    id
    ipAddress
    rangeStart
    rangeEnd
    status
    createdAt
    updatedAt
    deactivatedAt
    service {
      id
      name
      description
    }
  }
}
```

**Response Example**:

```json
{
  "data": {
    "ipByAddress": {
      "id": "10",
      "ipAddress": "185.180.14.10",
      "rangeStart": null,
      "rangeEnd": null,
      "status": "active",
      "createdAt": "2024-10-01T11:12:13",
      "updatedAt": "2024-10-03T09:21:33",
      "deactivatedAt": null,
      "service": {
        "id": "1",
        "name": "ChannelX",
        "description": "IP addresses for ChannelX services"
      }
    }
  }
}
```

### 4. Fetch IP Address by Range

You can also query for an IP address by providing an IP within a range.

**Query Example**:

```graphql
{
  ipByAddress(address: "185.180.14.5") {
    id
    ipAddress
    rangeStart
    rangeEnd
    status
    createdAt
    updatedAt
    deactivatedAt
    service {
      id
      name
      description
    }
  }
}
```

**Response Example**:

```json
{
  "data": {
    "ipByAddress": {
      "id": "33",
      "ipAddress": null,
      "rangeStart": "185.180.14.0",
      "rangeEnd": "185.180.14.255",
      "status": "active",
      "createdAt": "2024-10-10T09:15:00",
      "updatedAt": null,
      "deactivatedAt": null,
      "service": {
        "id": "2",
        "name": "Sellers",
        "description": "IP addresses for seller connections"
      }
    }
  }
}
```

## Error Handling

### Invalid IP Address

If an invalid IP address is passed, the API will return an error message.

**Example**:

```graphql
{
  ipByAddress(address: "999.999.999.999") {
    id
  }
}
```

**Response Example**:

```json
{
  "errors": [
    {
      "message": "'999.999.999.999' is not a valid IP address.",
      "locations": [
        {
          "line": 2,
          "column": 3
        }
      ]
    }
  ],
  "data": null
}
```

## Additional Details

- **IP Address Fields**:
  - `ipAddress`: Holds a single IP address (or null if it's a range).
  - `rangeStart`, `rangeEnd`: Used to define the start and end of an IP range.
  - `status`: Indicates whether the IP is `active` or `inactive`.
  - `createdAt`, `updatedAt`, `deactivatedAt`: Timestamps for when the IP was created, last updated, or deactivated.

- **Service Fields**:
  - `id`: The unique identifier of the service.
  - `name`: The name of the service.
  - `description`: A brief description of the service.

## Conclusion

This API allows querying both individual IPs and IP ranges, with detailed relationships to services. It ensures robust validation of inputs and provides detailed responses, including the status and timestamps of IP addresses.
