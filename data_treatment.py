import datetime


# Get very simple match info and let it structured to insert directly into the database.
def get_match_info(data):
    """
    Function to get simplified information from a match.

    Args:
        data (dict): Receives a dict containing the data of a given match.

    Returns:
        dict: Filtered dictionary with useful information from the match.
    """
    match_info = {
        "match_id": [data["metadata"]["matchId"]],
        "match_start": [
            datetime.datetime.fromtimestamp(data["info"]["gameCreation"] / 1000)
        ],
        "match_duration": [data["info"]["gameDuration"]],
        "match_winner": [data["info"]["teams"][0]["win"]],
        "match_surrender": [data["info"]["participants"][0]["gameEndedInSurrender"]],
        "match_remake": [data["info"]["participants"][0]["gameEndedInEarlySurrender"]],
    }
    return match_info


# Get very simple player info and structure it to insert into the database..
def get_player_info(data):
    """
    Function to get simple player information and structure it.

    Args:
        data (dict): Receives a dict containing the data of a given match.

    Returns:
        List[Dict]: Returns a list of dictionaries, each containing the information about a player that was on a given match.
    """
    player_array = []
    # Loop through each participant and fetch it's data.
    for participant in data["info"]["participants"]:
        player_info = {
            "puuid": participant["puuid"],
            "summoner_id": participant["summonerId"],
            "game_name": participant["riotIdGameName"],
            "tag_line": participant["riotIdTagline"],
            "profile_icon_id": participant["profileIcon"],
            "summoner_level": participant["summonerLevel"],
        }
        player_array.append(player_info)
    return player_array


# Function to return more detailed information about the player, including rating, account id, summoner_level, etc.
def get_player_rating(p_rating):
    """
    Returns the treated player's rating.

    Args:
        p_rating (dict): Information about the player perfomance in the 5v5 Solo Duo.

    Returns:
        dict: The filtered dictionary with the player's rating filtered.
    """
    player_rating = {
        "tier": p_rating["tier"],
        "division": p_rating["rank"],
        "league_points": p_rating["leaguePoints"],
        "wins": p_rating["wins"],
        "losses": p_rating["losses"],
        "last_rating": datetime.datetime.now().strftime("%Y-%m-%d"),
    }
    return player_rating


# Get informations from each player of a game and return it as a array.
def get_player_stats(data):
    """
    Function to get the stats for each player of a game.

    Args:
        data (dict): Receives a dict containing the data of a given match.

    Returns:
        List[Dict]: Returns a list of dictionaries with the stats of each player.
    """
    player_array = []
    # Loop through each participant and fetch it's data.
    for participant in data["info"]["participants"]:
        player_stats = {
            # Imutable global ID, unique for each account.
            "player_id": participant["puuid"],
            # ID of a given match. Should appear 10 times, one for each player.
            "match_id": data["metadata"]["matchId"],
            "champion_id": participant[
                "championId"
            ],  # ID of the champion played by the player.
            # KDA information.
            "kills": participant["kills"],
            "deaths": participant["deaths"],
            "assists": participant["assists"],
            "kda": participant["challenges"]["kda"],
            # Gold stats.
            "gold_earned": participant["goldEarned"],
            "gold_spent": participant["goldSpent"],
            "gold_per_minute": participant["challenges"]["goldPerMinute"],
            # Damage stats.
            "damage_per_minute": participant["challenges"]["damagePerMinute"],
            "total_damage_dealt_to_champions": participant[
                "totalDamageDealtToChampions"
            ],
            # Farm and vision stats.
            "neutral_minions_killed": participant["neutralMinionsKilled"],
            "total_minions_killed": participant["totalMinionsKilled"],
            "total_cs": int(
                participant["totalMinionsKilled"]
            )  # Calculation between the total minions and neutral minions killed.
            + int(participant["neutralMinionsKilled"]),
            "cs_per_min": (
                int(participant["totalMinionsKilled"])
                + int(participant["neutralMinionsKilled"])
            )
            / (int(data["info"]["gameDuration"]) / 60),
            # Vision stats.
            "vision_score": participant["visionScore"],
            "vision_score_per_min": participant["challenges"]["visionScorePerMinute"],
            "control_wards_placed": participant["challenges"]["controlWardsPlaced"],
            "wards_placed": participant["wardsPlaced"],
            "wards_killed": participant["wardsKilled"],
            # Game informations.
            "individual_position": participant["individualPosition"],
            # Player team, if it equals 200, return true, otherwise 0. Blue team is stored as 0 and red as 1 on the Database.
            "team": participant["teamId"] == 200,
        }
        player_array.append(player_stats)
    return player_array
