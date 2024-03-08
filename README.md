# PYLEAGUE

This is a simple project that I started developing to learn Python, being my first experience with the language and it's ecosystem.
The main goal of the project is simply fill a mysql database with data fetched from the RIOT API.

## Usage

A .env file containing the API KEY and database connection parameters are needed.
The only requirements to start the project are:

1. The following should be installed with pip:

- mysql-connector-python.
- pandas
- requests.
- sqlalchemy

2. The connection to the Database is required and a valid api key needs to be provided.
3. A initial value for the player info should be provided beforehand. (By inserting a PUUID and Username)

## Structure

The current structure of the project is really simple, just the basics to start to fetch the informations.

### TODO:

Multiple adjustments could be done to the code to improve it, some as follows:

- Add a stop condition to the code, in order to avoid leaving at the database writing and then not fetch the remaining data of a match.
- Add additional modules for different tasks, such as data analysis with Pandas, graph generation, etc.
- Add support for Match V5 timeline, improving the depth of the fetched data.
- Evaluate the possibility of changes in the tables structure, by, for example, calculating the KDA, total cs and fields dependant on time during the fetching process of the data to minimize the storage cost.
- Improve the amount and quality of the fetched data, by adding more API endpoints to be fetched, such as Summoner V4, to get the summoner level, profile icon (For front-end uses), account id, etc.
- Improve treatment of errors.
- Start the fetching without the need to manually add the first player info. Could be done by fetching a random player of a League by using the LEAGUE-V4 API, preferably from the Challenger League.
