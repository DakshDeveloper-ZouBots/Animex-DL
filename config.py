# Configuration Settings
import os

class Config:
    API_ID = int(os.environ.get("API_ID", "36428426"))
    API_HASH = os.environ.get("API_HASH", "30cba30aa38699e77ce264365e327528")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8647394346:AAGXTzKR6vJPOMXVika7IAAOIwSGETQOBB0")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://animekyoto:W5Itr6v2bZ3KpQF8@cluster0.trg5dtc.mongodb.net/?appName=Cluster0")
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "wzgram_db")
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1003702226466"))
    ADMINS = [int(x) for x in os.environ.get("ADMINS", "7957802698").split() if x.isdigit()]
