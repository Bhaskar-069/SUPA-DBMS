import mysql.connector
from config import Config

def init_database():
    # Connect to MySQL server
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD
    )
    cursor = conn.cursor()

    # Create database if it doesn't exist
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
    cursor.execute(f"USE {Config.MYSQL_DB}")

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(120) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS advice (
            id INT AUTO_INCREMENT PRIMARY KEY,
            question TEXT NOT NULL,
            savage_response TEXT NOT NULL,
            likes INT DEFAULT 0,
            dislikes INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_vote (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            advice_id INT NOT NULL,
            vote BOOLEAN NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (advice_id) REFERENCES advice(id),
            UNIQUE KEY user_advice_unique (user_id, advice_id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!") 