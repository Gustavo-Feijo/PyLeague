import mysql.connector
import os
import pandas as pd
import sqlalchemy

from datetime import date
from dotenv import load_dotenv
from mysql.connector import Error

# Load the dotenv configuration for the database connection.
load_dotenv("credentials.env")
# Creates a empty connection.
connection = None

# Connection string for the sqlalchemy.
connection_string = f"mysql+mysqlconnector://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_DATABASE')}"
engine = sqlalchemy.create_engine(connection_string)


# Connect to the mysql database.
def connect_mysql():
    global connection
    # Set the global connection as the mysql connection (If successful).
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
        )
    except Error as e:
        print("Error connecting to mysql: ", e)


# Function to close the mysql connection.
def close_mysql():
    global connection
    if connection and connection.is_connected():
        connection.close()


# Execute a query on the database.
def execute_query(query, params=None):
    global connection
    try:

        # Creates a cursor and executes the query.
        if connection is not None:
            cursor = connection.cursor()
        if params:
            cursor.execute(query, (params,))
        else:
            cursor.execute(query)

        data = cursor.fetchall()

        cursor.close()

        connection.commit()
        return data
    except Error as e:
        print("Error executing query: ", e)
        raise Error


# Get the next avaible puuid for fetching.
def get_next_puuid():
    sql = (
        """SELECT puuid FROM tb_player_info ORDER BY last_fetch ASC, id ASC LIMIT 1 """
    )
    try:
        puuid = execute_query(sql)
        # Returns the first element of the tuple inside the list, since it's only one possible return value.
        return puuid[0][0]
    except Exception as e:
        raise e


# Verify if a match was fetched before by checking the count of match_id on the database.
def is_match_on_db(match_id):
    sql = """ SELECT COUNT(*) FROM tb_match_info where match_id = %s"""
    match_on_db = execute_query(sql, match_id)
    if match_on_db is not None:
        # Returns false if the element is not found on the DB. [0][0] since the return is a tuple inside a list.
        if match_on_db[0][0] == 0:
            return False
        else:
            return True
    else:
        return None


# Verify if a player was already added to the database before.
def is_player_on_db(puuid):
    sql = """ SELECT COUNT(*) FROM tb_player_info WHERE puuid = %s"""
    player_on_db = execute_query(sql, puuid)
    if player_on_db is not None:
        # Returns the first element of the tuple inside the list, since it's only one possible return value.
        if player_on_db[0][0] == 0:
            return False
        else:
            return True
    else:
        return None


# Get the id of the player based on the puuid.
def get_player_id(puuid):
    sql = """SELECT id FROM tb_player_info WHERE puuid = %s"""
    player_id = execute_query(sql, puuid)
    return player_id[0][0]


# Get the id of a match based on the match_id.
def get_match_id(match_id):
    sql = """SELECT id FROM tb_match_info where match_id = %s"""
    match = execute_query(sql, match_id)
    return match[0][0]


# Get the date of the last fetch on a given player.
def get_last_fetch(puuid):
    sql = """SELECT last_fetch FROM tb_player_info WHERE puuid = %s"""
    date = execute_query(sql, puuid)
    return date[0][0]


# Function to update the last_fetch date for a given player.
def update_fetch_date(puuid):
    sql = """UPDATE tb_player_info SET last_fetch = CURDATE() WHERE puuid = %s"""
    execute_query(sql, puuid)


# Function to insert a match into the database.
def insert_match_info(match_info):
    df = pd.DataFrame(match_info)
    df.to_sql("tb_match_info", con=engine, if_exists="append", index=False)


# Function to insert a player array into the database, filtering the already existing players.
def insert_player_info(player_info):
    df = pd.DataFrame(player_info)
    mask = df["puuid"].apply(is_player_on_db)
    filtered = df[~mask].copy()
    filtered.to_sql("tb_player_info", con=engine, if_exists="append", index=False)


# Function to insert the player stats for a given game.
def insert_player_stats(match_stats):
    df = pd.DataFrame(match_stats)
    # Apply to the dataframe the function to get the int IDs assigned for the PUUID and MatchID.
    df["player_id"] = df["player_id"].apply(get_player_id)
    df["match_id"] = df["match_id"].apply(get_match_id)
    df.to_sql("tb_player_stats", con=engine, if_exists="append", index=False)
