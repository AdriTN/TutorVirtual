from ..database.database import get_connection

def create_users_table():
    connection = get_connection()
    cursor = connection.cursor()
    
    # Crear tabla de usuarios locales
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
    
    # Crear tabla de usuarios para almacenar info de cada proveedor
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_providers (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFENCES users(id) ON DELETE CASCADE,
            provider VARCHAR(50) NOT NULL,
            provider_user_id VARCHAR(255) NOT NULL,
            UNIQUE(provider_user_id, provider)
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token VARCHAR(255) NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    
    connection.commit()
    cursor.close()
    connection.close()