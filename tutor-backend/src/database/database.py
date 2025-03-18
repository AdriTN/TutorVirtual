import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    connection = psycopg2.connect(
        dsn=os.getenv("DATABASE_URL"),
        client_encoding='utf8')
    
    return connection
