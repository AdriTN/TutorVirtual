from ..database.database import get_connection

def create_users_table():
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            password VARCHAR(200) NOT NULL
        );
    """)
    
    connection.commit()
    cursor.close()
    connection.close()