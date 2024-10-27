import pytest
import requests

# Define the base URL for the API
BASE_URL = "http://localhost:8000"  

# Test for authorization endpoint
def test_authorization_endpoint():
    # Define the endpoint URL
    auth_url = f"{BASE_URL}/token"

    ### FIRST TEST
    # Set the username and password to give as arguments to the endpoint
    payload_1 = {
        "username": "user2",
        "password": "mon_mot_de_passe"
    }
    
    # Send a POST request to the authorization endpoint
    response_1 = requests.post(auth_url, data=payload_1)
    
    # Assert that the status code returned is 200
    assert response_1.status_code == 200, f"Expected status code 200 but got {response_1.status_code}"
    
    ### SECOND TEST
    # Set the username and password to give as arguments to the endpoint
    payload_2 = {
        "username": "unknown_user",
        "password": "mon_mot_de_passe"
    }
    
    # Send a POST request to the authorization endpoint
    response_2 = requests.post(auth_url, data=payload_2)
    
    # Assert that the status code returned is 200
    assert response_2.status_code == 400, f"Expected status code 200 but got {response_2.status_code}"
