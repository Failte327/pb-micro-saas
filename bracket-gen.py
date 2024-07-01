from bracketool.single_elimination import SingleEliminationGen
from bracketool.domain import *
from pprint import pprint
import requests

print("Fetching player ratings...")
search_url = f"player/v1.0/search"
competitor_list = []
default_rating = float("3.5")

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
        if doubles_rating == "NR":
            doubles_rating = default_rating
        else:
            doubles_rating = float(search_result["result"]["hits"][0]["ratings"]["doubles"])
        player_name = search_result["result"]["hits"][0]["fullName"]
        new_comp = Competitor(name=player_name, team=player_name, rating=doubles_rating)
        competitor_list.append(new_comp)
    else:
        print(f"No entry found for {i}")

gen = SingleEliminationGen(
    use_three_way_final=False,
    third_place_clash=True,
    use_rating=True,
    use_teams=True,
    random_seed=42
)

output = gen.generate(competitor_list)

pprint(output.rounds[0])
