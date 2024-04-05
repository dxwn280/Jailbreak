import os
import discord
import requests
import xml.etree.ElementTree as ET
import json
import aiohttp
from discord.ext import commands
from discord import app_commands
from discord_webhook import DiscordWebhook

intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix="/", intents=intents)

with open('config.json') as config_file:
    config_data = json.load(config_file)
WEBHOOKURL = config_data['webhook']

# XML STUFF # Function to scrape XML data from API
XML_API_URL = "https://edgegamers.gameme.com/api/serverinfo/104.128.58.156:27015/players/status"

def scrape_xml():
    response = requests.get(XML_API_URL)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        # Find the <map> element inside <server> inside <serverinfo>
        map_data = root.find('.//server/map').text
        player_data = root.find('.//server/act').text
        return map_data, player_data
    else:
        return None, None  # Returning None values if fetching XML data fails



# Command: /map
@client.hybrid_command(help="Displays the current map of the game server", usage="/map")
async def map(ctx: commands.Context):
    if ctx.guild is None:
        guild_name = "Private Messages"
    else:
        guild_name = ctx.guild.name  # Get guild name
        guild_id = ctx.guild.id # Get guild id
        guild_ownerid = ctx.guild.owner_id # Get owner of server id
        guild_owner = ctx.guild.owner # Get owner name

    # Get the current timestamp in UTC
    current_time = discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    if ctx.guild is None:
        detective_info = f'~~~\n{current_time} \n{ctx.author} ({ctx.author.id}) Used the command: /map \nServer: ({guild_name})' #this is for the webhook
    else:
        detective_info = f'~~~\n{current_time} \n{ctx.author} ({ctx.author.id}) Used the command: /map \nName: ({guild_name}) \nID: ({guild_id}) \nOwner: ({guild_owner}) \nID: ({guild_ownerid})' #this is for the webhook

    map_info, player_info = scrape_xml()  # Call scrape_xml() once and unpack the tuple
    if map_info is not None and player_info is not None:
        # Convert player_info to integer for comparison
        player_count = int(player_info)
        if player_count > 0:
            message = 'Map: ' + map_info + ' | Players: ' + player_info
            await ctx.send(message)
        elif player_count == 0:
            message = 'Players: ' + player_info + '\nServer either has no players or gameme/server is down'
            await ctx.send(message)

    # Print detective_info to the terminal
    print(detective_info)

    webhook_url = WEBHOOKURL 
    webhook = DiscordWebhook(url=webhook_url, content=detective_info) #this sends webhooks
    response = webhook.execute()

    return detective_info

