import requests
from requests.auth import HTTPBasicAuth
import json
import jsonpath
import pytest

def test_admin_usermod_users():
    url = "http://localhost:8765/evcharge/api/login"
    file = open("admin_creds.json", 'r')
    json_input = file.read()
    request_json = json.loads(json_input)
    response = requests.post(url,request_json)
    assert response.status_code == 200
    tok_en = (response.json())["token"]

    #admin/usermod
    #add new user with admin/usermod
    response = requests.post("http://localhost:8765/evcharge/api/admin/usermod/TestUser/TestPassword/User", headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200
    
    #pass invalid role to admin/usermod
    response = requests.post("http://localhost:8765/evcharge/api/admin/usermod/TestUser/TestPassword/Writer", headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 400

    #change user's password and role with admin/usermod
    response = requests.post("http://localhost:8765/evcharge/api/admin/usermod/TestUser/TestPassword2/Privileged", headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

    #admin/users
    #check user's data with admin/users
    response = requests.get("http://localhost:8765/evcharge/api/admin/users/TestUser", headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

    #check invalid user's data with admin/users
    response = requests.get("http://localhost:8765/evcharge/api/admin/users/TestUser42", headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 400

    #logout
    response = requests.post("http://localhost:8765/evcharge/api/logout", headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

def test_admin_sessionsupd():
    url = "http://localhost:8765/evcharge/api/login"
    file = open("admin_creds.json", 'r')
    json_input = file.read()
    request_json = json.loads(json_input)
    response = requests.post(url,request_json)
    assert response.status_code == 200
    tok_en = (response.json())["token"]

    #admin/system/sessionsupd
    #pass csv file when only json is supported
    response = requests.post("http://localhost:8765/evcharge/api/admin/system/sessionsupd", data={'file': 'echarge\\backend\\testing\\empty.csv'}, headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 400

    #pass json file with wrong fields
    response = requests.post("http://localhost:8765/evcharge/api/admin/system/sessionsupd", data={'file': 'echarge\\backend\\testing\\user.json'}, headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 400

    #pass right file with data
    response = requests.post("http://localhost:8765/evcharge/api/admin/system/sessionsupd", data={'file': 'echarge\\backend\\testing\\dummy_sessions.json'}, headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

    #logout
    response = requests.post("http://localhost:8765/evcharge/api/logout", headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

def test_sessions_per():
    url = "http://localhost:8765/evcharge/api/login"
    file = open("dummy_user.json", 'r')
    json_input = file.read()
    request_json = json.loads(json_input)
    response = requests.post(url,request_json)
    assert response.status_code == 200
    tok_en = (response.json())["token"]

    #SessionsPerPoint
    #check sessions for a point
    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerPoint/5f6978b800355e4c01059523/00010101/30000101",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerPoint/5f6978b800355e4c01059523/00010101/30000101" + "?format=" + "json",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerPoint/5f6978b800355e4c01059523/00010101/30000101" + "?format=" + "csv",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerPoint/5f6978b800355e4c01059523/00010101/30000101" + "?format=" + "docx",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 400

    #SessionsPerStation
    #check sessions for a station
    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerStation/2389/00010101/30000101",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerStation/2389/00010101/30000101" + "?format=" + "json",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerStation/2389/00010101/30000101" + "?format=" + "csv",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerStation/2389/00010101/30000101" + "?format=" + "docx",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 400

    #SessionsPerEV
    #check sessions for a e-vehicle
    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerEV/EV1/00010101/30000101",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerEV/EV1/00010101/30000101" + "?format=" + "json",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerEV/EV1/00010101/30000101" + "?format=" + "csv",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerEV/EV1/00010101/30000101" + "?format=" + "docx",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 400

    #SessionsPerProvider
    #check sessions for a provider
    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerProvider/09876543211/00010101/30000101",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerProvider/09876543211/00010101/30000101" + "?format=" + "json",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerProvider/09876543211/00010101/30000101" + "?format=" + "csv",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200

    response = requests.get("http://localhost:8765/evcharge/api/SessionsPerProvider/09876543211/00010101/30000101" + "?format=" + "docx",  headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 400

    #logout
    response = requests.post("http://localhost:8765/evcharge/api/logout", headers={'X-OBSERVATORY-AUTH':tok_en})
    assert response.status_code == 200