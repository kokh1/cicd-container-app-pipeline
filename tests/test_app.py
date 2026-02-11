#this is a file that runs tests using pytest to ensure endpoints are working
#simple unit/integration test

import pytest
from app import app

@pytest.fixture
def client(): 
    with app.test_client() as client: 
        yield client

def test_homepage(client): 
    response = client.get('/', follow_redirects=False)
    print("Redirect status:", response.status_code)
    print("Final URL:", response.headers.get("Location"))
    #assert that it redirects successfully to /joke
    assert response.status_code == 302
    assert response.headers["Location"] == "/joke"
    #follow the redirect manually
    final = client.get(response.headers["Location"])
    print("Final status:", final.status_code)
    assert final.status_code == 200

def test_joke_endpoint(client): 
    response = client.get('/joke')
    assert response.status_code == 200
    json_data = response.get_json()
        #this extracts the json data from the response
    assert "setup" in json_data
        #this checks if the key "setup" is in the json data
    assert "punchline" in json_data
        #this checks if the key "punchline" is in the json data
    assert "type" in json_data
        #this checks if the key "type" is in the json data

