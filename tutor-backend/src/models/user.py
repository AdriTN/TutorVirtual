from ..database.database import get_connection

def create_users_table():
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(50) NOT NULL,
            password VARCHAR(50) NOT NULL
        );
    """)
    
    connection.commit()
    cursor.close()
    connection.close()