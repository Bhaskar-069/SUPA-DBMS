import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32))
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    COHERE_API_KEY = os.getenv('COHERE_API_KEY', 'dwdlq71agDUBvTOIimXYPbwgbdQlawO3L1fOACfk') 