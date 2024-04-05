import discord
import json
from discord.ext import commands
from commands import map as map_commands

intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix="/", intents=intents)

with open('config.json') as config_file:
    config_data = json.load(config_file)
TOKEN = config_data['token']

# Event: Bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

# Import and register the map commands from map.py
client.add_command(map_commands.map)

client.run(TOKEN)
