from bracketool.domain import *
from flask import Flask, request, render_template
import requests

app = Flask(__name__)

auth_token = ""

@app.route('/')
def home():
    return render_template("home.html")

# dupr auth
@app.route('/make_get_request', methods=['POST'])
def get():
    global auth_token
    base_url = "https://api.dupr.gg/"
    auth_endpoint = "auth/v1.0/login"
    provided_endpoint = request.json.get("endpoint")
    if auth_token == "":
        auth_url = f"{base_url}{auth_endpoint}"
        # credentials go here
        data = {}
        response = requests.post(auth_url, json=data)
        json = response.json()
        auth_token = json["result"]["accessToken"]
        if auth_token != "":
            print(f"auth token: {auth_token}")
    requested = requests.get(f"{base_url}{provided_endpoint}", headers={"Authorization": f"Bearer {auth_token}"})
    if requested.status_code == 200:
        print(requested.json())
        return requested.json()
    else:
        print("Response code from dupr was not 200")
        return "Response code from dupr was not 200"

@app.route('/make_post_request', methods=['POST'])
def post():
    global auth_token
    base_url = "https://api.dupr.gg/"
    auth_endpoint = "auth/v1.0/login"
    provided_endpoint = request.json.get("endpoint")
    provided_data = request.json.get("data")
    if auth_token == "":
        auth_url = f"{base_url}{auth_endpoint}"
        # credentials go here
        data = {}
        response = requests.post(auth_url, json=data)
        json = response.json()
        print(json)
        auth_token = json["result"]["accessToken"]
        if auth_token != "":
            print(f"auth token: {auth_token}")
    requested = requests.post(f"{base_url}{provided_endpoint}", headers={"Authorization": f"Bearer {auth_token}"}, json=provided_data)
    if requested.status_code == 200:
        return requested.json()
    else:
        print("Response code from dupr was not 200")
        return("Response code from dupr was not 200")

@app.route('/parse_csv', methods=["POST"])
def parse_csv():
    print("Fetching player ratings...")
    search_url = f"player/v1.0/search"
    competitor_list = []
    # player_list = request.form.get("playername").split(",")
    data = request.files.get("csv_upload").read().decode("utf-8")
    player_list = data.split(",")
    counter = 0
    for i in player_list:
        if i is not None:
            new = i.strip().lower()
            player_list[counter] = new
            counter = counter + 1

    for i in player_list:
        if i is not None:
            if i != "":
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

                response = requests.post("http://127.0.0.1:10000/make_post_request", json=data)

                print(response)
                search_result = response.json()

                print(search_result)

                # Goes through the matching search results, picks the first one, grabs their doubles rating
                if search_result["result"]["hits"] != []:
                    doubles_rating = search_result["result"]["hits"][0]["ratings"]["doubles"]
                    if doubles_rating == "NR":
                        doubles_rating = "Unknown"
                    else:
                        doubles_rating = float(search_result["result"]["hits"][0]["ratings"]["doubles"])
                    player_name = search_result["result"]["hits"][0]["fullName"]
                    competitor_list.append({player_name: doubles_rating})
                else:
                    print(f"No entry found for {i}")
                
                print(competitor_list)
    
    return competitor_list

# @app.route('/generate_bracket', methods=["POST"])
# def generate_bracket():
#     print("Fetching player ratings...")
#     search_url = f"player/v1.0/search"
#     competitor_list = []
#     default_rating = float("3.5")
#     player_list = request.form.get("playername").split(",")
#     counter = 0
#     for i in player_list:
#         new = i.strip().lower()
#         player_list[counter] = new
#         counter = counter + 1

#     print(player_list)

#     for i in player_list:
#         query_data = {
#             "limit":10,
#             "offset":0,
#             "query":f"{i}",
#             "exclude":[],
#             "includeUnclaimedPlayers":True,
#             "filter":{
#                 "lat":40.114955,
#                 "lng":-111.654923,
#                 "rating":{
#                     "maxRating":None,
#                     "minRating":None
#                     },
#                 "locationText":""
#                 }
#         }

#         data = {
#             "endpoint": search_url,
#             "data": query_data
#         }

#         response = requests.post("http://127.0.0.1:10000/make_post_request", json=data)

#         print(response)
#         search_result = response.json()

#         # Goes through the matching search results, picks the first one, grabs their doubles rating
#         if search_result["result"]["hits"] != []:
#             doubles_rating = search_result["result"]["hits"][0]["ratings"]["doubles"]
#             if doubles_rating == "NR":
#                 doubles_rating = default_rating
#             else:
#                 doubles_rating = float(search_result["result"]["hits"][0]["ratings"]["doubles"])
#             player_name = search_result["result"]["hits"][0]["fullName"]
#             new_comp = Competitor(name=player_name, team=player_name, rating=doubles_rating)
#             competitor_list.append(new_comp)
#         else:
#             print(f"No entry found for {i}")

#     gen = SingleEliminationGen(
#         use_three_way_final=False,
#         third_place_clash=True,
#         use_rating=True,
#         use_teams=True,
#         random_seed=42
#     )

#     output = gen.generate(competitor_list)

#     print(output.rounds[0])
    
#     clashes = {}
#     clash_number = 0
#     for n in output.rounds[0]:
#         competitor_a = n.competitor_a.name
#         if n.competitor_b is not None:
#             competitor_b = n.competitor_b.name
#         else:
#             competitor_b = "BYE"
#         clashes[clash_number] = f"{competitor_a},{competitor_b}"
#         clash_number = clash_number + 1
#     return clashes