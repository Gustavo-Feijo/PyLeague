import mysql.connector
import os
import pandas as pd
import sqlalchemy

from datetime import datetime
from dotenv import load_dotenv
from mysql.connector import Error

# Load the dotenv configuration for the database connection.
load_dotenv("credentials.env")
# Creates a empty connection.
connection = None

# Connection string for the sqlalchemy.
connection_string = f"mysql+mysqlconnector://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_DATABASE')}"
engine = sqlalchemy.create_engine(connection_string)

"""
    Module with the operations needed to insert, fetch and update data from the database.
    Most of the operations have the following pattern:

    Args: 
    VOID => Functions that will always run a pre defined sql statement.
    PUUID OR MATCH_ID => Functions that will fetch players/match data from the database or verify if the data was already inserted.
    DICTIONARYS => Functions that will receive pre filtered dictionaries ready to be inserted into the database.

    Raises:
    Most of the function will raise the mysql exceptions, since most of them use the execute_query function.
"""


# Connect to the mysql database.
def connect_mysql():
    """
    Connect to the mysql database with the credentials from the enviroment.
    """
    global connection
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
        )
    except Error as err:
        raise err


# Function to close the mysql connection.
def close_mysql():
    """
    References the global connection, verify that it exists and is connected, if it is, close the connection.
    """
    global connection
    if connection and connection.is_connected():
        connection.close()


# Execute a query on the database.
def execute_query(query, params=None):
    """
    Execute a query on the database. Verifies the connection, if it's connected creates a cursor anr proceeds to execute the query.

    Args:
        query (string): String containing the query to execute.
        params (tuples, optional): Receives a tuble with the values to be passed to the database alongside the SQL query. Defaults to None.

    Raises:
        Exception: Raises any exception raised by the mysql.

    Returns:
        List[tuples]: Returns a list of tuples containing the results.
    """
    global connection
    try:

        # Creates a cursor and executes the query.
        if connection is not None:
            cursor = connection.cursor()
        else:
            raise Exception("Could not create cursor, the database is not connected.")
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        data = cursor.fetchall()

        cursor.close()

        connection.commit()
        return data
    except Exception:
        raise Exception


# Create the tables if they don't exist.
def create_tables():
    """
    Function to create the tables if they don't exist already.
    Split the statements, remove any trailing whitespaces to avoid a wrong ; and execute the queries.
    """
    with open("create_statements.sql", "r") as sql_file:
        sql = sql_file.read()
        statements = sql.split(";")
        try:
            for statement in statements:
                if statement.strip():
                    execute_query(statement)
        except Exception as e:
            raise e


# Get the next avaible puuid for fetching.
def get_next_puuid():
    """
    Selects the first puuid when sorting by ascending fetch date and ascending id, getting the oldest puuid that wasn't fetched lately.
    """
    sql = (
        """SELECT puuid FROM tb_player_info ORDER BY last_fetch ASC, id ASC LIMIT 1 """
    )
    try:
        puuid = execute_query(sql)
        # Returns the first element of the tuple inside the list, since it's only one possible return value.
        return puuid[0][0]
    except Exception as e:
        raise e


# Verify if a match is on the database by checking the count of match_id on the database.
def is_match_on_db(match_id):
    """
    Args:
        match_id (string): Receives the id of a match to check against the database.

    Returns:
        bool: If the match was found on the database, returns TRUE, else returns FALSE.
    """
    sql = """ SELECT COUNT(*) FROM tb_match_info where match_id = %s"""
    try:
        match_on_db = execute_query(sql, (match_id,))
        if match_on_db is not None:
            # Returns false if the element is not found on the DB. [0][0] since the return is a tuple inside a list.
            if match_on_db[0][0] == 0:
                return False
            else:
                return True
        else:
            raise Exception("Could not verify the database")
    except Exception as e:
        raise e


# Verify if a player is already on the database before.
def is_player_on_db(puuid):
    """
    Args:
        puuid (string): Receives the unique id of a player to check against the database.

    Returns:
        bool: If the player was found on the database, returns TRUE, else returns FALSE.
    """
    sql = """ SELECT COUNT(*) FROM tb_player_info WHERE puuid = %s"""
    try:
        player_on_db = execute_query(sql, (puuid,))
        if player_on_db is not None:
            # Returns the first element of the tuple inside the list, since it's only one possible return value.
            if player_on_db[0][0] == 0:
                return False
            else:
                return True
        else:
            raise Exception("Could not verify the database")
    except Exception as e:
        raise e


# Get the id of the player based on the puuid.
def get_player_id(puuid):
    """
    Essential function. Returns the int id of a player that shares the same puuid as the passed.
    Don't do the checking for the existence of the player on the database.

    Returns:
        Integer: The int id of the player on the players table.
    """
    sql = """SELECT id FROM tb_player_info WHERE puuid = %s"""
    try:
        player_id = execute_query(sql, (puuid,))
        return player_id[0][0]
    except Exception as e:
        raise e


# Get the id of a match based on the match_id.
def get_match_id(match_id):
    """
    Essential function. Returns the int id of a match that shares the same match_id as the passed.
    Don't do the checking for the existence of the match on the database.

    Returns:
        Integer: The int id of the match on the matches table.
    """
    sql = """SELECT id FROM tb_match_info where match_id = %s"""
    try:
        match = execute_query(sql, (match_id,))
        return match[0][0]
    except Exception as e:
        raise e


# Get the date of the last fetch on a given player.
def get_last_fetch(puuid):
    """
    Function used for mantaining the control flow of the fetching process, so no player can have it's data fetched until all others players before him have it's data fetched.

    Returns:
        Date: Return the last date since the fetch of t he players data.
    """
    sql = """SELECT last_fetch FROM tb_player_info WHERE puuid = %s"""
    try:
        date = execute_query(sql, (puuid,))
        return date[0][0]
    except Exception as e:
        raise e


# Function to update the last_fetch date for a given player.
def update_fetch_date(puuid):
    """
    Update the last_fetch date for a given player after all his data was fetched.
    """
    sql = """UPDATE tb_player_info SET last_fetch = NOW() WHERE puuid = %s"""
    try:
        execute_query(sql, (puuid,))
    except Exception as e:
        raise e


# Function to insert a match into the database.
def insert_match_info(match_info):
    """
    Function that creates a pandas dataframe from a dictionary and insert it into the database with the sqlalchemy.

    Args:
        match_info (DICT): Dictionary carrying information about the match, pre formatted.

    Raises:
        Exception: Any exception caught during the dataframe creation or the sql insertion.
    """
    try:
        df = pd.DataFrame(match_info)
        df.to_sql("tb_match_info", con=engine, if_exists="append", index=False)
    except Exception as e:
        raise e


# Function to insert a player array into the database, filtering the already existing players.
def insert_player_info(player_info):
    """
    Function to insert a player into the database.
    Creates a mask by applying the is_player_on_db function, then proceeds to copy the data that didn't match the mask into a new filtered dataframe.
    Inserts the filtered dataframe into the database with the sqlalchemy.

    Args:
        player_info (DICT): Dictionary carrying information about the player, pre formatted.

    Raises:
        Exception: Any exception caught during the dataframe creation and manipulation or the sql insertion.
    """
    try:
        df = pd.DataFrame(player_info)
        mask = df["puuid"].apply(is_player_on_db)
        filtered = df[~mask].copy()
        filtered.to_sql("tb_player_info", con=engine, if_exists="append", index=False)
    except Exception as e:
        raise e


# Function to insert the player stats for a given game.
def insert_player_stats(player_stats):
    """
    Function to insert the player stats into the database.
    Get the integers player id and the match id from the database before doing the insertion by applying the function to the columns.
    Insert the data into the database with the sqlalchemy.

    Args:
        player_stats (List[Dict]): List carrying the individual stats for each player on a match, pre formatted.

    Raises:
        Exception: Any exception caught during the dataframe creation and manipulation or the sql insertion.
    """
    try:
        df = pd.DataFrame(player_stats)
        # Apply to the dataframe the function to get the int IDs assigned for the PUUID and MatchID.
        df["player_id"] = df["player_id"].apply(get_player_id)
        df["match_id"] = df["match_id"].apply(get_match_id)
        df.to_sql("tb_player_stats", con=engine, if_exists="append", index=False)
    except Exception as e:
        raise e


# Function to select all the data.
def get_all_stats():
    """
    Select all the data from the player_stats table.
    """
    global connection
    sql = """SELECT * FROM tb_player_stats"""
    try:
        df = pd.read_sql(sql, connection, index_col=["id"])
        return df
    except Exception as e:
        raise e


# Function to select all the data.
def get_all_players():
    """
    Select all the data from the player_info table.
    """
    global connection
    print(connection)
    sql = """SELECT * FROM tb_player_info"""
    try:
        df = pd.read_sql(sql, connection, index_col=["id"])
        return df
    except Exception as e:
        raise e


# Function to select all the data.
def get_all_matches():
    """
    Select all the data from the match_info table.
    """
    global connection
    sql = """SELECT * FROM tb_match_info"""
    try:
        df = pd.read_sql(sql, connection, index_col=["id"])
        return df
    except Exception as e:
        raise e


# Function to get the default value for the last fetch column.
def get_default_fetch_date():
    """
    Function to get the default value for the last fetch column.
    Retrieve it from the information_schema table and parse it into date.

    Returns:
        date: The default value for the last fetch column.
    """
    sql = """SELECT column_default FROM information_schema.columns WHERE table_schema = %s AND table_name = 'tb_player_info' AND column_name = 'last_fetch'"""
    try:
        default_fetch = execute_query(sql, (os.getenv("DB_DATABASE"),))
        default_fetch = default_fetch[0][0]
        to_date = datetime.strptime(default_fetch, "%Y-%m-%d %H:%M:%S")
        return to_date
    except Exception as e:
        raise e


# Function to verify if the database is empty or not.
def empty_db():
    """
    Function that gets the count of player on the database.

    Returns:
        bool: If the database is empty, returns true, otherwise returns false.
    """
    sql = """SELECT count(*) FROM tb_player_info"""
    try:
        count = execute_query(sql)
        if count[0][0] == 0:
            return True
        else:
            return False
    except Exception as e:
        raise e
