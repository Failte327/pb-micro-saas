from flask import Flask, request
import requests

app = Flask(__name__)

auth_token = ""

@app.route('/make_get_request', methods=['POST'])
def get():
    global auth_token
    base_url = "https://api.dupr.gg/"
    auth_endpoint = "auth/v1.0/login"
    provided_endpoint = request.json.get("endpoint")
    print(provided_endpoint)
    if auth_token == "":
        auth_url = f"{base_url}{auth_endpoint}"
        # credentials go here
        data = {}
        response = requests.post(auth_url, json=data)
        json = response.json()
        auth_token = json["result"]["accessToken"]
        print(json)
        print(auth_token)
    requested = requests.get(f"{base_url}{provided_endpoint}", headers={"Authorization": f"Bearer {auth_token}"})
    print(requested.json())
    return requested.json()

@app.route('/make_post_request', methods=['POST'])
def post():
    global auth_token
    base_url = "https://api.dupr.gg/"
    auth_endpoint = "auth/v1.0/login"
    provided_endpoint = request.json.get("endpoint")
    provided_data = request.json.get("data")
    print(provided_endpoint)
    if auth_token == "":
        auth_url = f"{base_url}{auth_endpoint}"
        # credentials go here
        data = {}
        response = requests.post(auth_url, json=data)
        json = response.json()
        auth_token = json["result"]["accessToken"]
        print(json)
        print(auth_token)
    requested = requests.post(f"{base_url}{provided_endpoint}", headers={"Authorization": f"Bearer {auth_token}"}, json=provided_data)
    print(requested.json())
    return requested.json()

    