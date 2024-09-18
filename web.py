from flask import Flask, request, render_template
from sqlalchemy import create_engine, text
from loguru import logger
import requests

app = Flask(__name__)

# Helper functions for filtering bad data out of the CSV file upload
def has_numbers(inputString):
        return any(char.isdigit() for char in inputString)

def no_symbols(inputString):
        return any(char.isalnum() for char in inputString)

# Initiating auth_token globally
auth_token = ""

# Creating database connection
engine = create_engine("sqlite:///auth_token.db")

# Checking database for existing auth_token
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM auth_token;"))
    if result.rowcount != 0:
        for row in result:
            if row.auth_token is not None:
                logger.info(f"Auth token found: {row.auth_token}")
                auth_token = row.auth_token
    else:
        logger.debug("No auth_token currently in database")

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/tools')
def tools():
    return render_template("tools.html")

# DUPR Request, grabs authentication token first and then submits the requested payload
@app.route('/make_get_request', methods=['POST'])
def get():
    global auth_token
    base_url = "https://api.dupr.gg/"
    auth_endpoint = "auth/v1.0/login"
    auth_url = f"{base_url}{auth_endpoint}"
    provided_endpoint = request.json.get("endpoint")
    data = {
            "email": "timothy.twelker@gmail.com",
            "password": "Shealyn15!"
    }
    if auth_token == "":
        response = requests.post(auth_url, json=data)
        json = response.json()
        auth_token = json["result"]["accessToken"]
        # Save auth_token to database
        if auth_token != "":
            with engine.connect() as conn:
                conn.execute(text(f"INSERT INTO auth_token ('auth_token') VALUES ('{auth_token}');"))
                conn.commit()
    # Request given to the endpoint
    requested = requests.get(f"{base_url}{provided_endpoint}", headers={"Authorization": f"Bearer {auth_token}"})
    if requested.status_code == 403:
        with engine.connect() as conn:
            conn.execute(text(f"DELETE FROM auth_token where auth_token = '{auth_token}';"))
            conn.commit()
            logger.success("Deleted expired auth_token")
            new_token_request = requests.post(auth_url, json=data)
            json = new_token_request.json()
            auth_token = json["result"]["accessToken"]
            new_get_request = requests.get(f"{base_url}{provided_endpoint}", headers={"Authorization": f"Bearer {auth_token}"})
            return new_get_request.json()
    elif requested.status_code == 200:
        return requested.json()
    else:
        logger.info(f"DUPR Response Code: {requested.status_code}")
        logger.info(f"DUPR Response Data: {requested.text}")
        return "Response code from dupr was not 200"

@app.route('/make_post_request', methods=['POST'])
def post():
    global auth_token
    base_url = "https://api.dupr.gg/"
    auth_endpoint = "auth/v1.0/login"
    auth_url = f"{base_url}{auth_endpoint}"
    provided_endpoint = request.json.get("endpoint")
    provided_data = request.json.get("data")
    data = {
            "email": "timothy.twelker@gmail.com",
            "password": "Shealyn15!"
    }
    if auth_token == "":
        response = requests.post(auth_url, json=data)
        json = response.json()
        auth_token = json["result"]["accessToken"]
        # Save auth_token to database
        if auth_token != "":
            with engine.connect() as conn:
                conn.execute(text(f"INSERT INTO auth_token ('auth_token') VALUES ('{auth_token}');"))
                conn.commit()
    # Request given to the endpoint
    requested = requests.post(f"{base_url}{provided_endpoint}", headers={"Authorization": f"Bearer {auth_token}"}, json=provided_data)
    if requested.status_code == 403:
        with engine.connect() as conn:
            conn.execute(text(f"DELETE FROM auth_token where auth_token = '{auth_token}';"))
            conn.commit()
            logger.success("Deleted expired auth_token")
            auth_token == ""
            new_token_request = requests.post(auth_url, json=data)
            json = new_token_request.json()
            auth_token = json["result"]["accessToken"]
            conn.execute(text(f"INSERT INTO auth_token ('auth_token') VALUES ('{auth_token}');"))
            conn.commit()
            new_post_request = requests.post(f"{base_url}{provided_endpoint}", headers={"Authorization": f"Bearer {auth_token}"}, json=provided_data)
            return new_post_request.json()
    elif requested.status_code == 200:
        return requested.json()
    else:
        logger.info(f"DUPR Response Code: {requested.status_code}")
        logger.info(f"DUPR Response Data: {requested.text}")
        return "Response code from dupr was not 200"

# CSV Parsing Endpoint, returns player list with associated doubles rating from DUPR
@app.route('/parse_csv', methods=["POST"])
def parse_csv():
    logger.info("Fetching player ratings...")
    search_url = f"player/v1.0/search"
    competitor_list = []
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
                if i != "#value!":
                    if "email" not in i:
                        if "start time" not in i:
                            if no_symbols(i) is True:
                                if has_numbers(i) is False:
                                    if i != "wait list":
                                        if i != "paid":
                                            if i != "guest":
                                                if "member" not in i:
                                                    if i != "total":
                                                        if "doubles" not in i:
                                                            if "singles" not in i:
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

                                                                search_result = response.json()

                                                                # Goes through the matching search results, picks the first one, if it matches the full name, grabs their doubles rating
                                                                if search_result["result"]["hits"] != []:
                                                                    if i == search_result["result"]["hits"][0]["fullName"].lower():
                                                                        doubles_rating = search_result["result"]["hits"][0]["ratings"]["doubles"]
                                                                        if doubles_rating == "NR":
                                                                            doubles_rating = "Unknown"
                                                                        else:
                                                                            doubles_rating = float(search_result["result"]["hits"][0]["ratings"]["doubles"])
                                                                        player_name = search_result["result"]["hits"][0]["fullName"]
                                                                        if {player_name: doubles_rating} not in competitor_list:
                                                                            competitor_list.append({player_name: doubles_rating})
                                                                else:
                                                                    logger.debug(f"No entry found for {i}")
    
    return competitor_list

# Player List Parsing Endpoint, returns player list with associated doubles rating from DUPR
@app.route('/player_list_search', methods=["POST"])
def player_list_search():
    logger.info("Fetching player ratings...")
    search_url = f"player/v1.0/search"
    competitor_list = []
    player_list = request.form.get("playername").split(",")
    counter = 0
    for i in player_list:
        new = i.strip().lower()
        player_list[counter] = new
        counter = counter + 1

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

        response = requests.post("http://127.0.0.1:10000/make_post_request", json=data)

        search_result = response.json()

        # Goes through the matching search results, picks the first one, if it matches the full name, grabs their doubles rating
        if search_result["result"]["hits"] != []:
            if i == search_result["result"]["hits"][0]["fullName"].lower():
                doubles_rating = search_result["result"]["hits"][0]["ratings"]["doubles"]
                if doubles_rating == "NR":
                    doubles_rating = "Unknown"
                else:
                    doubles_rating = float(search_result["result"]["hits"][0]["ratings"]["doubles"])
                player_name = search_result["result"]["hits"][0]["fullName"]
                # If player is not already in the list, append their data
                if {player_name: doubles_rating} not in competitor_list:
                    competitor_list.append({player_name: doubles_rating})
        else:
            logger.debug(f"No entry found for {i}")
    
    return competitor_list
