import os
import requests
import time
from dotenv import load_dotenv

# Loads the API KEY from the .env file and creates a session for the requests.
load_dotenv("credentials.env")
api_key = os.getenv("API_KEY")
session = requests.Session()


# Generic function to fetch the data from a given URL.
def fetch(url):
    # Continue to try to fetch the data until we get a ok response or a error different than the rate limit.
    while True:
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
                time.sleep(retry_after + 1)
            # If any other error occurs, raise an exception.
            else:
                raise Exception(f"Response failed with code: {response.status_code}")
        except Exception as e:
            print(e)
            return None


# Function to fetch the list of matches of a given player.
def fetch_matches(puuid, start_value, start_date):
    # Convert the start_date to Epoch timestamp, as used on the RIOT API.
    timestamp = int(start_date.timestamp())
    data = fetch(
        f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={timestamp}&queue=420&start={start_value}&count=100"
    )
    return data


# Function to fetch the data from a given match.
def fetch_match_data(match_id):
    data = fetch(f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}")
    return data
