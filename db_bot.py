import mysql.connector, os
from mysql.connector import Error
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
sqlUser = os.getenv('SQL_USER')
sqlPass = os.getenv('SQL_PASS')
hostname = 'localhost'
dbName = '8frames'
queries_suffix = "_queries"
query_selection_suffix = "_query_selection"


def create_server_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=hostname,
            user=sqlUser,
            passwd=sqlPass
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def create_db_connection(db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=hostname,
            user=sqlUser,
            passwd=sqlPass,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")  

def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

def insertIntoBotPosts(bot_post_id, trigger_post_id, channel_id, user_id, game, game_character, query, result, mobile):
    string = f"""
            INSERT INTO bot_post VALUES(
            "{bot_post_id}",
            "{trigger_post_id}",
            "{channel_id}",
            "{user_id}",
            "{game}",
            "{game_character}",
            "{query}",
            "{result}",
            {mobile})
        """
    connection = create_db_connection(dbName)
    try:
        execute_query(connection, string)
        return 1
    except:
        return -1

def getQueryAuthor(post_id):
    query = f"""
        SELECT user_id
        FROM bot_post
        WHERE bot_post_id = "{post_id}"
    """
    connection = create_db_connection(dbName)
    try:
       return read_query(connection, query)
    except:
        return -1

def getRowByBotMessage(post_id):
    query = f"""
        SELECT *
        FROM bot_post
        WHERE bot_post_id = "{post_id}"
    """
    connection = create_db_connection(dbName)
    try:
        return read_query(connection, query)[0]
    except:
        return -1
   
def updateQueryCount(query, game):
    query = query.lower()
    table = game + queries_suffix
    string = f"""
        UPDATE {table}
        SET search_quantity = search_quantity + 1
        WHERE query = "{query}"
    """
    connection = create_db_connection(dbName)
    try:
        execute_query(connection, string)
        return 1
    except:
        return -1

def createQueryRow(query, game):
    query = query.lower()
    table = game + queries_suffix
    string = f"""
        INSERT IGNORE INTO {table} VALUES (
        "{query}",
        0
    );
    """
    connection = create_db_connection(dbName)
    try:
        execute_query(connection, string)
        return 1
    except:
        return -1

def createQuerySelectionRow(query, game, result):
    query = query.lower()
    table = game + query_selection_suffix
    string = f"""
        INSERT IGNORE INTO {table} VALUES (
        "{query}",
        "{result}",
        0
    );
    """
    connection = create_db_connection(dbName)
    try:
        execute_query(connection, string)
        return 1
    except:
        return -1

def updateQuerySelectionCount(query, game, result):
    query = query.lower()
    table = game + query_selection_suffix
    string = f"""
        UPDATE {table}
        SET search_quantity = search_quantity + 1
        WHERE query = "{query}"
        AND query_selection = "{result}" 
    """
    connection = create_db_connection(dbName)
    try:
        execute_query(connection, string)
        return 1
    except:
        return -1

def getSearchResult(query, game):
    query = query.lower()
    table = "bot_post"
    string = f"""
        SELECT query_selection
        FROM {table}
        WHERE bot_post_id = "{query}"
    """
    connection = create_db_connection(dbName)
    try:
       return read_query(connection, string)[0][0]
    except:
        return -1

def correctQuery(query, game, result, message_id):
    message_id = str(message_id)
    best_guess = getSearchResult(message_id, game)
    query = query.lower()
    table = game + query_selection_suffix
    print(best_guess)
    string = f"""
        UPDATE {table}
        SET search_quantity = search_quantity - 1
        WHERE query = "{query}"
        AND query_selection = "{best_guess}"
    """
    connection = create_db_connection(dbName)
    try:
        execute_query(connection, string)
    except:
        return -1
    createQuerySelectionRow(query, game, result)
    updateQuerySelectionCount(query, game, result)
    string = f"""
        UPDATE bot_post
        SET query_selection = "{result}"
        WHERE bot_post_id = "{message_id}"
    """
    try:
        return execute_query(connection, string)
    except:
        return -1

def getMoveResultRatio(query, game):
    query = query.lower()
    table = game + queries_suffix
    string = f"""
        SELECT search_quantity
        FROM {table}
        WHERE query = "{query}"
    """
    connection = create_db_connection(dbName)
    try:
        totalUsage = read_query(connection, string)[0][0]
    except:
        return -1
    selection_table = game + query_selection_suffix
    string = f"""
        SELECT query_selection, search_quantity
        FROM {selection_table}
        WHERE query = "{query}"
    """
    try:
        usageSplit = read_query(connection, string)
    except:
        return -1
    percentages = {}
    for i in range(len(usageSplit)):
        percentages[usageSplit[i][0]] = (int(usageSplit[i][1])/int(totalUsage))*100
    return percentages


connection = create_server_connection()
print(connection)
cursor = connection.cursor()

#TMP
#cursor.execute('DROP DATABASE ' + dbName + ';')
#####


query = 'CREATE DATABASE IF NOT EXISTS ' + dbName + ';'
try:
    cursor.execute(query)
    print("Database created successfully")
except Error as err:
    print(f"Error: '{err}'")

create_bot_post_table = """
CREATE TABLE IF NOT EXISTS bot_post (
  bot_post_id VARCHAR(200) PRIMARY KEY NOT NULL,
  trigger_post_id VARCHAR(200) NOT NULL,
  channel_id VARCHAR(200) NOT NULL,
  user_id VARCHAR(200) NOT NULL,
  game VARCHAR(10) NOT NULL,
  game_character VARCHAR(20) NOT NULL,
  query VARCHAR(100) NOT NULL,
  query_selection VARCHAR(100) NOT NULL,
  mobile TINYINT(1) NOT NULL
  );
 """

connection = create_db_connection(dbName)
execute_query(connection, create_bot_post_table)

games = ['sf3', 'sf4', 'sfv', 't7']

for i in range(len(games)):
    queries_table_name = games[i] + "_queries"
    create_query_table = f"""
    CREATE TABLE IF NOT EXISTS {queries_table_name} (
    query VARCHAR(100) PRIMARY KEY NOT NULL,
    search_quantity INT NOT NULL
    );
    """

    execute_query(connection, create_query_table)

    selection_table_name = games[i] + "_query_selection"
    create_query_selection_table = f"""
    CREATE TABLE IF NOT EXISTS {selection_table_name} (
    query VARCHAR(100) NOT NULL,
    FOREIGN KEY(query) REFERENCES {queries_table_name} (query),
    query_selection VARCHAR(100) NOT NULL,
    PRIMARY KEY(query, query_selection),
    search_quantity INT NOT NULL
    );
    """

    execute_query(connection, create_query_selection_table)
