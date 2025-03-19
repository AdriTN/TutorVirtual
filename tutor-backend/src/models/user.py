from ..database.database import get_connection

def create_users_table():
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(120) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            is_admin BOOLEAN NOT NULL DEFAULT false,
            
            CONSTRAINT chk_name_min_length CHECK (LENGTH(username) >= 3),
            CONSTRAINT chk_password_complexity CHECK (password ~* '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,}$')
        );
    """)
    
    connection.commit()
    cursor.close()
    connection.close()