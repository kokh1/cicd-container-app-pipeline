#this is a file that runs tests using pytest to ensure endpoints are working
#simple unit/integration test

import pytest
from app import app

@pytest.fixture
def client(): 
    with app.test_client() as client: 
        yield client

def test_homepage(client): 
    response = client.get('/')
    assert response.status_code == 200
    assert b"Hello, World!" in response.data

def test_joke_endpoint(client): 
    response = client.get('/joke')
    assert response.status_code == 200
    json_data = response.get_json()
        #this extracts the json data from the response
    assert "setup" in json_data
        #this checks if the key "setup" is in the json data
    assert "punchline" in json_data
        #this checks if the key "punchline" is in the json data

