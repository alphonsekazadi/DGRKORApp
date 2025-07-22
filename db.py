# db.py

import psycopg2
from config import DB_CONFIG

def get_connection(instance_name):
    config = DB_CONFIG[instance_name]
    conn = psycopg2.connect(
        host=config["host"],
        port=config["port"],
        dbname=config["dbname"],
        user=config["user"],
        password=config["password"]
    )
    return conn
