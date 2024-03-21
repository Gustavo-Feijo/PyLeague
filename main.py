# Import the functions on the other modules.
import concurrent.futures
from data_treatment import *
from db_operations import *
from fetch import *


# Function to be run through the threads.
def worker(match):
    """
    Function to fetch the data and insert into the database.

    Args:
        match (string): Match_id from the match to be fetched.
    """
    try:
        if is_match_on_db(match):
            return

        print(f"Starting fetch for the match: {match}")
        match_data = fetch_match_data(match)

        if match_data is not None:

            new_p_info = []
            m_info = get_match_info(match_data)
            p_info = get_player_info(match_data)
            p_stats = get_player_stats(match_data)

            for player in p_info:
                if is_player_on_db(player["puuid"]) and last_rating_today(
                    player["puuid"]
                ):
                    continue

                summoner_id = player["summoner_id"]
                p_rating = get_player_rating(fetch_player_rating(summoner_id))

                if is_player_on_db(player["puuid"]):
                    update_rating(p_rating, player["puuid"])
                    update_rating_date(player["puuid"])
                    continue

                player.update(p_rating)

                new_p_info.append(player)
                update_rating_date(player["puuid"])
            insert_match_info(m_info)
            insert_player_info(new_p_info)
            insert_player_stats(p_stats)
        print("Finished data fetching from the match:", match)

    except Exception as e:
        print("Error getting data from the match:", match, " with error: ", e)


# Try block to get the user interruption of the code.
try:
    # Create the connection to the mysql database.
    # Create the tables if they don't exist.
    connect_mysql()
    create_tables()

    # Verify if there is any player on the database whose puuid equals it's puuid.
    # Only returns false if the database is empty.
    if empty_db():
        firstPUUID = fetch_top_challenger()
        fetch_date = get_default_fetch_date()

    # Infinite loop to get the data.
    while True:
        puuid = None
        last_fetch = None
        # Try to get the next puuid from the database.
        try:
            puuid = get_next_puuid()
            last_fetch = get_last_fetch(puuid)
        except Exception as e:
            print("Error getting next puuid:", e)
            print("Fetching the top one of the soloq")
        finally:
            if not puuid:
                puuid = firstPUUID
                last_fetch = fetch_date

        # Creates the match list to be populated, the count to keep track of the current depth of the match list and the date of the last time this puuid was fetched.
        match_list = []
        count = 0
        # Infinite loop that gets the match list of the current player until all the matchs are found.
        try:
            while True:
                # Fetch 100 matches after the count and attach to the full match list. Last fetch is passed to only get matches after the last time it was fetched.
                matches = fetch_matches(puuid, count, last_fetch)
                match_list.extend(matches)
                # If the retrieved matches has 100 matches, then we go to the next iteration to get the remaining.
                if matches is not None and len(matches) == 100:
                    count += 100
                else:
                    break
        except Exception as e:
            print("Error getting the match list: ", e)
            break
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_match = {
                executor.submit(worker, match): match for match in match_list
            }

        # If every match was succesfully read and inserted, then update the last_fetch from the given player.
        update_fetch_date(puuid)
        print("Starting next loop...")
except KeyboardInterrupt:
    print("User interrupted the program.")
except Error as E:
    print("A error occurred: %s", E)
finally:
    # Close the mysql connection.
    close_mysql()
