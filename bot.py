# Main Entry Point
import logging
from wzgram import Client
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WzgramBot")

class Bot(Client):
    def __init__(self):
        super().__init__(
            "WzgramBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="plugins")
        )

    async def start(self):
        await super().start()
        logger.info("Bot started successfully!")

    async def stop(self, *args):
        await super().stop()
        logger.info("Bot stopped.")

if __name__ == "__main__":
    Bot().run()
