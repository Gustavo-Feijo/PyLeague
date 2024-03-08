import datetime


# Get very simple match info and let it structured to insert directly into the database.
def get_match_info(data):
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
    player_array = []
    # Loop through each participant and fetch it's data.
    for participant in data["info"]["participants"]:
        match_info = {
            "puuid": participant["puuid"],
            "game_name": participant["summonerName"],
        }
        player_array.append(match_info)
    return player_array


# Get informations from each player of a game and return it as a array.
def get_player_stats(data):
    player_array = []
    # Loop through each participant and fetch it's data.
    for participant in data["info"]["participants"]:
        player_info = {
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
        }
        player_array.append(player_info)
    return player_array
