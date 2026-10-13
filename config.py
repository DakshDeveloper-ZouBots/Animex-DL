# Configuration Settings
import os

class Config:
    API_ID = int(os.environ.get("API_ID", "123456"))
    API_HASH = os.environ.get("API_HASH", "your_api_hash")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "wzgram_db")
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-100"))
    ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split() if x.isdigit()]
