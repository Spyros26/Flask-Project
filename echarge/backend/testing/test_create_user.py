import requests
from requests.auth import HTTPBasicAuth
import json
import jsonpath
import pytest



def test_create_new_user():
    url = "http://localhost:8765/evcharge/api/sign-up"
    file = open("user.json", 'r')
    json_input = file.read()
    request_json = json.loads(json_input)
    response = requests.post(url,request_json)
    assert response.status_code == 200
    requests.get("http://localhost:8765/evcharge/api/Logout")
    assert response.status_code == 200
    #print(response.url)

def test_login_with_auth():
    url="http://localhost:8765/evcharge/api/"
    new_response = requests.get("http://localhost:8765/evcharge/api/statement_filters",auth=HTTPBasicAuth("User1","password1"))
    assert new_response.status_code == 200
    requests.get("http://localhost:8765/evcharge/api/Logout")
    #print(new_response.url)
    assert new_response.status_code == 200

def test_login_and_charge():
    url = "http://localhost:8765/evcharge/api/"
    file = open("charge.json", 'r')
    json_input = file.read()
    request_json = json.loads(json_input)
    response = requests.post(url, request_json,auth=HTTPBasicAuth("User1","password1"))
    assert response.status_code == 200
    requests.get("http://localhost:8765/evcharge/api/Logout")
    #print(response.url)

def test_statement_filters():
    url = "http://localhost:8765/evcharge/api/statement_filters"
    file = open("dates.json", 'r')
    json_input = file.read()
    request_json = json.loads(json_input)
    response = requests.post(url, request_json, auth=HTTPBasicAuth("User1", "password1"))
    assert response.status_code == 200
    requests.get("http://localhost:8765/evcharge/api/Logout")

