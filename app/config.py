import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_CX = os.getenv("GOOGLE_CX")
    CHELGU_NEWS_URL = os.getenv("CHELGU_NEWS_URL")
    CACHE_TTL = int(os.getenv("CACHE_TTL", 600))
