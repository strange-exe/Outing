# db.py
import mysql.connector
import json

# Load config.json
with open("config.json") as f:
    config = json.load(f)

def get_db_connection():
    """Creates and returns a new database connection for each request."""
    try:
        connection = mysql.connector.connect(
            host=config["DB_HOST"],
            user=config["DB_USER"],
            password=config["DB_PASSWORD"],
            database=config["DB_NAME"]
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None