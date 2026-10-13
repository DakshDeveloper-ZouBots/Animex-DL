# MongoDB Connection Adapter
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

class Database:
    def __init__(self, uri, database_name):
        self._client = AsyncIOMotorClient(uri)
        self._db = self._client[database_name]
        self.users = self._db["users"]

    async def add_user(self, user_id):
        if not await self.is_user_exist(user_id):
            await self.users.insert_one({"_id": user_id})

    async def is_user_exist(self, user_id):
        user = await self.users.find_one({"_id": user_id})
        return bool(user)

db = Database(Config.MONGO_URI, Config.DATABASE_NAME)
