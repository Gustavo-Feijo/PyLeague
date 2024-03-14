# Import the functions on the other modules.
from data_treatment import *
from db_operations import *
from fetch import *

# Create the connection to the mysql database.
# Create the tables if they don't exist.

# Try block to get the user interruption of the code.
try:
    connect_mysql()
    create_tables()
    # Infinite loop to get the data.
    while True:
        # Try to get the next puuid from the database.
        try:
            puuid = get_next_puuid()
        except Exception as e:
            print("Error getting next puuid:", e)
            break

        # Creates the match list to be populated, the count to keep track of the current depth of the match list and the date of the last time this puuid was fetched.
        match_list = []
        count = 0
        last_fetch = get_last_fetch(puuid)

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

                # Get the JSON data from the match.
                match_data = fetch_match_data(match)

                # If the data of the match was fetched, proceed to process it and then insert into the database.
                if match_data is not None:
                    insert_match_info(get_match_info(match_data))
                    insert_player_info(get_player_info(match_data))
                    insert_player_stats(get_player_stats(match_data))
                else:
                    continue

            except Exception as e:
                print("Error getting data from the match:", match, " with error: ", e)

        # If every match was succesfully read and inserted, then update the last_fetch from the given player.
        update_fetch_date(puuid)
except KeyboardInterrupt:
    print("User interrupted the program.")
except Error as E:
    print("A error occurred: %s", e)
finally:
    # Close the mysql connection.
    close_mysql()
