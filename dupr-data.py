import requests


print("Fetching player ratings...")
search_url = f"player/v1.0/search"
player_ratings = {}

# Sample list from a recent open play event
player_list = []

for i in player_list:
    query_data = {
        "limit":10,
        "offset":0,
        "query":f"{i}",
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
    if search_result["result"]["hits"] != []:
        doubles_rating = search_result["result"]["hits"][0]["ratings"]["doubles"]
        player_name = search_result["result"]["hits"][0]["fullName"]

        player_ratings[player_name] = doubles_rating
    else:
        print(f"No entry found for {i}")

print(player_ratings)