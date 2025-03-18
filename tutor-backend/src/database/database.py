import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        connection = psycopg2.connect(
        dsn=os.getenv("DATABASE_URL"),
        client_encoding='utf8')
        
        return connection
    except Exception as e:
        print(f"Error: {e}")
        return None
