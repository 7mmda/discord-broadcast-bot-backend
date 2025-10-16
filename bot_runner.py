import discord
from discord.ext import commands
import threading
import asyncio
import os

intents = discord.Intents.default()
intents.members = True  # Enable the members intent to access member list
intents.presences = True # Enable the presences intent to access member statuses
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user.name} ({bot.user.id})')
    print('------')

def run_bot(token):
    """
    Run the Discord bot in a separate thread.
    """
    try:
        bot.run(token)
    except Exception as e:
        print(f"Error running bot: {e}")

def start_bot_thread(token):
    """
    Start the bot in a background thread.
    """
    bot_thread = threading.Thread(target=run_bot, args=(token,), daemon=True)
    bot_thread.start()
    return bot

def get_bot_instance():
    """
    Get the bot instance.
    """
    return bot

