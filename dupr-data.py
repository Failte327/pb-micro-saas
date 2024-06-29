import requests

player_id = "8105602894"

search_url = f"player/v1.0/search"

# Change query to whatever the player's name is
query_data = {
    "limit":10,
    "offset":0,
    "query":"*",
    "exclude":[],
    "includeUnclaimedPlayers":True,
    "filter":{
        "lat":40.114955,
        "lng":-111.654923,
        "rating":{
            "maxRating":None,
            "minRating":None
            },
        "locationText":""
        }
}

data = {
    "endpoint": search_url,
    "data": query_data
}

response = requests.post("http://127.0.0.1:5000/make_post_request", json=data)

search_result = response.json()

# Goes through the matching search results, picks the first one, grabs their doubles rating
doubles_rating = search_result["result"]["hits"][0]["ratings"]["doubles"]
player_name = search_result["result"]["hits"][0]["fullName"]

print(player_name)
print(doubles_rating)