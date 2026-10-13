# Start & Help Plugin Handlers
from wzgram import Client, filters
from wzgram.types import Message
from script import Dead
from database.db import db

@Client.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    await db.add_user(message.from_user.id)
    mention = message.from_user.mention
    await message.reply_text(Dead.START_MSG.format(mention=mention))

@Client.on_message(filters.command("help"))
async def help_handler(client: Client, message: Message):
    mention = message.from_user.mention
    await message.reply_text(Dead.HELP_TXT.format(mention=mention))
