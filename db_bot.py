import mysql.connector, os
from mysql.connector import Error
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
sqlUser = os.getenv('SQL_USER')
sqlPass = os.getenv('SQL_PASS')
hostname = 'localhost'
dbName = '8frames'

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

def insertIntoBotPosts(bot_post_id, trigger_post_id, channel_id, user_id, game, game_character, query, mobile):
    string = f"""
            INSERT INTO bot_post VALUES
            (NULL, {bot_post_id}, {trigger_post_id}, "{channel_id}", "{user_id}", "{game}", "{game_character}", "{query}", {mobile})
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
    return read_query(connection, query)
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
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  bot_post_id VARCHAR(200) NOT NULL,
  trigger_post_id VARCHAR(200) NOT NULL,
  channel_id VARCHAR(200) NOT NULL,
  user_id VARCHAR(200) NOT NULL,
  game VARCHAR(10) NOT NULL,
  game_character VARCHAR(20) NOT NULL,
  query VARCHAR(100) NOT NULL,
  mobile TINYINT(1) NOT NULL
  );
 """

connection = create_db_connection(dbName)
execute_query(connection, create_bot_post_table)

#print(insertIntoBotPosts(123, 456, 't7', '1,2'))
