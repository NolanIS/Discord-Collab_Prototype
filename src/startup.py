import os
from dotenv import load_dotenv
import discord

from Discord.collab_bot import CollabBot
from Storage.storage_manager import StorageManager


def load_env():
    load_dotenv()
    discord_token = os.getenv("DISCORD_TOKEN")
    database_location = os.getenv("DATABASE_LOCATION")
    return discord_token, database_location


def create_bot():
    return CollabBot(command_prefix="/", intents=discord.Intents.all())

def setup():
    discord_token, database_location = load_env()
    StorageManager(database_location)


    bot = create_bot()
    bot.run(discord_token)



setup()
