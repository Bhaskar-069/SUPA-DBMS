import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32))
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '1973')
    MYSQL_DB = os.getenv('MYSQL_DB', 'advice_db')
    COHERE_API_KEY = os.getenv('COHERE_API_KEY', 'dwdlq71agDUBvTOIimXYPbwgbdQlawO3L1fOACfk') 