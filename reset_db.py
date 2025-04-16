import mysql.connector
from config import Config

def reset_database():
    # Connect to MySQL server
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD
    )
    cursor = conn.cursor()

    # Drop database if exists and create new one
    cursor.execute(f"DROP DATABASE IF EXISTS {Config.MYSQL_DB}")
    cursor.execute(f"CREATE DATABASE {Config.MYSQL_DB}")
    cursor.execute(f"USE {Config.MYSQL_DB}")

    # Create tables
    cursor.execute("""
        CREATE TABLE user (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(120) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE advice (
            id INT AUTO_INCREMENT PRIMARY KEY,
            question TEXT NOT NULL,
            response TEXT NOT NULL,
            mode VARCHAR(20) NOT NULL DEFAULT 'savage',
            likes INT UNSIGNED DEFAULT 0,
            dislikes INT UNSIGNED DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE user_vote (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            advice_id INT NOT NULL,
            vote_type ENUM('like', 'dislike') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (advice_id) REFERENCES advice(id),
            UNIQUE KEY user_advice_unique (user_id, advice_id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database has been reset and reinitialized successfully!")

if __name__ == "__main__":
    reset_database() 