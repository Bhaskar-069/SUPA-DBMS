import os

class Config:
    SECRET_KEY = os.urandom(32)
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '1973'
    MYSQL_DB = 'advice_db'
    COHERE_API_KEY = 'dwdlq71agDUBvTOIimXYPbwgbdQlawO3L1fOACfk' 