import os
import requests
import time
from dotenv import load_dotenv

# Loads the API KEY from the .env file and creates a session for the requests.
load_dotenv("credentials.env")
api_key = os.getenv("API_KEY")
session = requests.Session()

retry_after = 0


# Generic function to fetch the data from a given URL.
def fetch(url):
    """
    Function that fetches the data from the URL passed as parameter.
    Continuously fetches the data until a response is received or a error different than 429 occurs.
    If the error is 429, wait till the api call limit refreshes.

    Args:
        url (string): The URL of the API endpoint.

    Returns:
        Dict: Returns the dict received from the API.
        NONE: Returns none if any other error is returned.
    """
    while True:
        global retry_after
        if retry_after > 0:
            time.sleep(retry_after + 1)
            retry_after = 0
        try:
            # Does a GET request with the given URL and api key on the header.
            response = session.get(url, headers={"X-Riot-Token": f"{api_key}"})
            # If the response was successful, just return it.
            if response.status_code == 200:
                return response.json()
            # If the response was unsuccessful with the status code 429, then the rate limit was reached.
            # A retry after header is going to be received, so the code will sleep until it's possible to do a retry.
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                print(
                    f"Rate limit exceeded. Waiting for {retry_after} seconds before retrying..."
                )
            # If any other error occurs, raise an exception.
            else:
                raise Exception(f"Response failed with code: {response.status_code}")
        except Exception as e:
            print(e)
            return None


# Function to fetch the list of matches of a given player.
def fetch_matches(puuid, start_value, start_date):
    """
    Function that receives a array of matches from the server.

    Args:
        puuid (string): The player whose matches will be fetched.
        start_value (integer): How many matches were already fetched, starting to fetch after it.
        start_date (date): Date to start fetching match data. Converts to timestamp format, which is used by the server.

    Returns:
        Dict: Returns the dict received from the API.
        NONE: Returns none if any other error is returned to the fecth function.
    """
    timestamp = int(start_date.timestamp())
    data = fetch(
        f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={timestamp}&queue=420&start={start_value}&count=100"
    )
    return data


# Function to fetch the data from a given match.
def fetch_match_data(match_id):
    """
    Function to fetch the data from a given match from the server.

    Args:
        match_id (string): The ID of the match to fetch.

    Returns:
        Dict: Returns the dict received from the API.
        NONE: Returns none if any other error is returned to the fecth function.
    """
    data = fetch(f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}")
    return data


# Function to fetch data from a given player.
def fetch_player_details(summoner_id):
    """
    Function to fetch the data from a given player.

    Args:
        summoner_id (string):  Encrypted summoner ID. Max length 63 characters.

    Returns:
        Dict: Returns the dict received from the API.
    """

    data = fetch(
        f"https://br1.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}"
    )
    return data


def fetch_player_rating(summoner_id):
    """
    Function to fetch the current rating of a given player.
    Receives a list with all the queues for the given player, returns only the soloqueue.
    Args:
        summoner_id (string): Encrypted summoner ID. Max length 63 characters.

    Returns:
        Dict: Returns the dict received from the API.
    """
    data = fetch(
        f"https://br1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
    )
    if data is not None:
        for queue in data:
            if queue["queueType"] == "RANKED_SOLO_5x5":
                data = queue
    return data


def fetch_top_challenger():
    """
    Function to fetch the player details of the player with most points on the Challenger queue, fetching the player info based on the summoner id and returning the puuid.

    Returns:
        string: Returns the PUUID of the player with most points on the Challenger queue.
    """
    data = fetch(
        "https://br1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
    )
    max_lp = max(
        range(len(data["entries"])), key=lambda i: data["entries"][i]["leaguePoints"]
    )
    top_one = data["entries"][max_lp]["summonerId"]
    player_data = fetch_player_details(top_one)
    return player_data["puuid"]


def get_retry_after():
    return retry_after
