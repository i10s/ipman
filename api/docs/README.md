
# IP Management Service - GraphQL API

## Overview

This project provides a Python service that exposes a GraphQL API for managing IP addresses and services. The service allows querying individual IPs, IP ranges, their statuses (active/inactive), and linking them to different services. The project includes robust input validation, read-only enforcement, security measures, and detailed API documentation.

## Features

- Query individual IP addresses or ranges.
- Fetch associated services for IP addresses.
- Track the status of IPs (active/inactive).
- Prevent mutations, enforcing a read-only API.
- Health check endpoint to ensure the API and database are operational.

## Project Structure

```bash
├── src                # Source code for the IP Management service
│   ├── app.py         # Main entry point for the Flask server
│   ├── database       # Contains database connection setup and models
│   ├── graphql_api    # GraphQL schema and resolvers
├── tests              # Unit tests for the service
│   └── test_app.py    # Tests for the core functionality and GraphQL queries
├── docker             # Docker configuration files
│   ├── Dockerfile     # Dockerfile for building the service
│   ├── docker-compose.yml # Compose file to set up the service with Docker
├── README.md          # This README file
└── API_DOCS.md        # Documentation for the GraphQL API
```

## Requirements

- Python 3.9+
- PostgreSQL
- Docker
- Flask
- Graphene
- Ariadne
- SQLAlchemy

### Setup Instructions

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-repo/ip-management.git
   cd ip-management
   ```

2. **Set up Python Virtual Environment (optional but recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**

   ```bash
   poetry install
   ```

4. **Configuration:**
   Ensure the configuration for the PostgreSQL database and Consul server is correct by updating environment variables or `.env` files as needed.

5. **Run the Service Locally:**

   ```bash
   python src/app.py
   ```

   Alternatively, you can use Docker for easy setup:

   ```bash
   docker-compose up --build
   ```

6. **Access the API:**
   The GraphQL API will be accessible at:
   - `http://localhost:5000/graphql` for the API
   - `http://localhost:5000/health` for the health check endpoint.

## GraphQL API Usage

### Sample Queries

1. **Fetch All Services:**

   ```graphql
   {
     services {
       id
       name
       description
     }
   }
   ```

2. **Fetch All IP Addresses:**

   ```graphql
   {
     ipAddresses {
       id
       ipAddress
       rangeStart
       rangeEnd
       status
     }
   }
   ```

3. **Fetch a Specific IP Address:**

   ```graphql
   {
     ipByAddress(address: "185.180.14.1") {
       id
       ipAddress
       status
       service {
         name
         description
       }
     }
   }
   ```

### Error Handling

If an invalid IP address is provided, the service will return an appropriate error message:

```graphql
{
  "errors": [
    {
      "message": "'999.999.999.999' is not a valid IP address."
    }
  ]
}
```

## Testing the Service

### Running Unit Tests

To run the unit tests for the project, use the following command:

```bash
pytest
```

This will execute the tests located in the `/tests` directory.

Example tests:

- Test database interactions for querying IPs and services.
- Test GraphQL queries for correct data return.
- Error handling for invalid input.

## Deployment

This project is designed to run as a Docker container. Use the provided `docker-compose.yml` file for easy deployment. Ensure that your environment variables for the PostgreSQL database are properly set.

### Steps to Deploy

1. Build the Docker image:

   ```bash
   docker-compose build
   ```

2. Start the containers:

   ```bash
   docker-compose up
   ```

The API will be available at `http://localhost:5000`.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
