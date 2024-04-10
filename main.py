import discord
import json
from discord.ext import commands
from commands import map as map_command
from commands import players as players_command

intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix="/", intents=intents)

with open('config.json') as config_file:
    config_data = json.load(config_file)
TOKEN = config_data['token']
OWNER = int(config_data['owner'])

# Import and register the map commands from map.py
client.add_command(map_command.map)
client.add_command(players_command.players)

# Event: Bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    await client.tree.sync() #this syncs all the commands available to the command tree on start

client.run(TOKEN)
