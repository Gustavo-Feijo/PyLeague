# Import the functions on the other modules.
from data_treatment import *
from db_operations import *
from fetch import *


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
                try:
                    # Fetch 100 matches after the count and attach to the full match list. Last fetch is passed to only get matches after the last time it was fetched.
                    matches = fetch_matches(puuid, count, last_fetch)
                    match_list.extend(matches)
                    # If the retrieved matches has 100 matches, then we go to the next iteration to get the remaining.
                    if matches is not None and len(matches) == 100:
                        count += 100
                    else:
                        break
                except Exception as e:
                    raise Exception(e)
        except Exception as e:
            print("Error getting the match list: ", e)
            break

        # Loop through each match on the previous fetched match list.
        for match in match_list:
            try:
                # Verify if the match was not fetched before, if it was, jump to the next match on the list.
                if is_match_on_db(match):
                    continue

                print("Fetching data from the match: ", match)
                # Get the DICT data from the match.
                match_data = fetch_match_data(match)

                # If the data of the match was fetched, proceed to process it and then insert into the database.
                if match_data is not None:
                    # Array to receive the players data whose ratings where not fetched lately.
                    new_p_info = []
                    # Get the simple data for each table.
                    m_info = get_match_info(match_data)
                    p_info = get_player_info(match_data)
                    p_stats = get_player_stats(match_data)
                    # p_info is an array of dicts, containing each player on the game.
                    for player in p_info:
                        # Verify if the player is on the DB and if didn't had the rating fetched already.
                        if is_player_on_db(player["puuid"]) and last_rating_today(
                            player["puuid"]
                        ):
                            continue
                        # Gets the summoner id to use for retrieving the player's rating and treat it.
                        summoner_id = player["summoner_id"]
                        p_rating = get_player_rating(fetch_player_rating(summoner_id))
                        player.update(p_rating)

                        # Append the player's array without the duplicates and update the date of the rating fetching.
                        new_p_info.append(player)
                        update_rating_date(player["puuid"])
                    print("Inserting data into the database:")
                    # Insert the data into the database.
                    insert_match_info(m_info)
                    insert_player_info(new_p_info)
                    insert_player_stats(p_stats)
                else:
                    continue

            except Exception as e:
                print("Error getting data from the match:", match, " with error: ", e)

        # If every match was succesfully read and inserted, then update the last_fetch from the given player.
        update_fetch_date(puuid)
        os.system("cls" if os.name == "nt" else "clear")
        print("Starting next loop...")
except KeyboardInterrupt:
    print("User interrupted the program.")
except Error as E:
    print("A error occurred: %s", E)
finally:
    # Close the mysql connection.
    close_mysql()
