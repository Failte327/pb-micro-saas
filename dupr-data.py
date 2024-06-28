import requests

player_id = "16OGL0"

search_url = f"player/v1.0/{player_id}"

data = {
    "endpoint": search_url
}

response = requests.post("http://127.0.0.1:10000/make_request", json=data)

print(response)