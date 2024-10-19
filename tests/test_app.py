# Unit tests for the application
# File: /tests/test_app.py

import pytest
from app import app
from database.models import Service, IPAddress
from flask import json

# Define a fixture for the test client
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Test the /health endpoint
def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"database": "connected", "status": "healthy"}

# Test fetching all services
def test_fetch_all_services(client):
    query = '''
    {
        allServices {
            id
            name
            description
        }
    }
    '''
    response = client.post('/graphql', json={'query': query})
    assert response.status_code == 200
    data = response.json['data']['allServices']
    assert isinstance(data, list)  # Should return a list of services

# Test querying for a valid IP address
def test_valid_ip_query(client):
    query = '''
    {
        ipByAddress(address: "185.180.14.1") {
            id
            ipAddress
            status
            service {
                name
            }
        }
    }
    '''
    response = client.post('/graphql', json={'query': query})
    assert response.status_code == 200
    data = response.json['data']['ipByAddress']
    assert data['ipAddress'] == "185.180.14.1"
    assert data['status'] == "active"
    assert data['service']['name'] == "ChannelX"

# Test querying for an invalid IP address
def test_invalid_ip_query(client):
    query = '''
    {
        ipByAddress(address: "999.999.999.999") {
            id
        }
    }
    '''
    response = client.post('/graphql', json={'query': query})
    assert response.status_code == 200
    assert response.json['data']['ipByAddress'] is None  # Should return null

# Test querying for a non-existent IP address
def test_non_existent_ip_query(client):
    query = '''
    {
        ipByAddress(address: "192.168.1.1") {
            id
            ipAddress
        }
    }
    '''
    response = client.post('/graphql', json={'query': query})
    assert response.status_code == 200
    assert response.json['data']['ipByAddress'] is None  # Should return null
