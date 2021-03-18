import requests
import json
import jsonpath
import pytest



def test_create_new_user():
    url = "http://localhost:8765/evcharge/api/sign-up"
    file = open("user.json", 'r')
    json_input = file.read()
    request_json = json.loads(json_input)
    response = requests.post(url,request_json)
    assert response.status_code == 400

def test_login_user():
    url = "http://localhost:8765/evcharge/api/Login"
    file = open("user2.json", 'r')
    json_input = file.read()
    request_json = json.loads(json_input)
    response = requests.post(url,request_json)
    assert response.status_code == 200

def test_failed_login_user():
    url = "http://localhost:8765/evcharge/api/Login"
    file = open("user3.json", 'r')
    json_input = file.read()
    request_json = json.loads(json_input)
    response = requests.post(url,request_json)
    assert response.status_code == 400

def test_logout():
    url = "http://localhost:8765/evcharge/api/Logout"
    response = requests.get(url)
    assert response.status_code == 200



