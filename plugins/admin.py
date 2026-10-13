# Admin Management Commands Plugin
from wzgram import Client, filters
from wzgram.types import Message
from config import Config

@Client.on_message(filters.command("stats") & filters.user(Config.ADMINS))
async def stats_handler(client: Client, message: Message):
    await message.reply_text("<b>Bot is running smoothly. All systems operational.</b>")
